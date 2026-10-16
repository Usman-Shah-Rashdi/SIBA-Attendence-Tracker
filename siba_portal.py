
from dataclasses import dataclass
from math import ceil
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


LOGIN_PATH = "Default.aspx"
ATTENDANCE_PATH = "wpAttendance.aspx"
SEMESTER_FIELD = "ctl00$ContentPlaceHolder1$Dpsemester"
COURSE_FIELD = "ctl00$ContentPlaceHolder1$DpCmscourses"
ATTENDANCE_SUBMIT_FIELD = "ctl00$ContentPlaceHolder1$Button1"
MINUTES_PER_UNIT = 50
ALLOWED_ABSENCE_UNITS = 12


class PortalError(RuntimeError):
    """Base error for SIBA portal communication failures."""


class PortalLoginError(PortalError):
    """Raised when the portal rejects the supplied credentials."""


class PortalResponseError(PortalError):
    """Raised when the portal returns an unexpected page."""


def _hidden_fields(soup: BeautifulSoup) -> dict[str, str]:
    return {
        field["name"]: field.get("value", "")
        for field in soup.select("form#form1 input[type=hidden][name]")
    }


def _options(
    soup: BeautifulSoup,
    field_name: str,
) -> list[dict[str, str | bool]]:
    select = soup.find("select", {"name": field_name})
    if not select:
        return []
    return [
        {
            "name": option.get_text(" ", strip=True),
            "value": option.get("value", ""),
            "selected": option.has_attr("selected"),
        }
        for option in select.find_all("option")
    ]


def parse_attendance_html(html: str) -> dict[str, Any]:
    """Extract attendance records from a SIBA attendance HTML response."""

    soup = BeautifulSoup(html, "html.parser")

    def selected_option(select_name: str) -> dict[str, str] | None:
        select = soup.find("select", {"name": select_name})
        if not select:
            return None

        option = select.find("option", selected=True)
        if not option:
            option = select.find("option")

        if not option:
            return None

        return {
            "name": option.get_text(" ", strip=True),
            "value": option.get("value", ""),
        }

    semester = selected_option(
        "ctl00$ContentPlaceHolder1$Dpsemester"
    )
    subject = selected_option(
        "ctl00$ContentPlaceHolder1$DpCmscourses"
    )

    # Locate the attendance table using its ASP.NET-generated ID.
    table = soup.find(
        "table",
        id=lambda value: value and "RadGrid1_ctl00" in value
    )

    if not table:
        raise ValueError(
            "Attendance table not found. "
            "The response may be a login page or an unexpected page."
        )

    headers = [
        cell.get_text(" ", strip=True).lower()
        for cell in table.select("thead th, thead td")
    ]

    required_headers = [
        "s.no",
        "attendacne date",
        "from time",
        "present",
        "class minutes",
    ]

    if not all(header in headers for header in required_headers):
        raise ValueError(
            f"Unexpected attendance table columns: {headers}"
        )

    records = []

    for row in table.select("tbody tr"):
        cells = row.find_all("td", recursive=False)

        if len(cells) != len(headers):
            continue

        values = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        record = dict(zip(headers, values))

        status = record["present"].strip().lower()
        if status not in {"present", "absent"}:
            continue

        try:
            minutes = int(record["class minutes"])
        except (TypeError, ValueError):
            minutes = None

        records.append({
            "number": record["s.no"],
            "date": record["attendacne date"],
            "time": record["from time"],
            "status": status.title(),
            "minutes": minutes,
        })

    present_units = sum(
        (r["minutes"] or 0) / MINUTES_PER_UNIT
        for r in records
        if r["status"] == "Present"
    )
    absent_units = sum(
        (r["minutes"] or 0) / MINUTES_PER_UNIT
        for r in records
        if r["status"] == "Absent"
    )
    total_units = present_units + absent_units

    return {
        "semester": semester,
        "subject": subject,
        "records": records,
        "summary": {
            "present": sum(r["status"] == "Present" for r in records),
            "absent": sum(r["status"] == "Absent" for r in records),
            "total": len(records),
            "present_units": present_units,
            "absent_units": absent_units,
            "total_units": total_units,
            "allowed_absence_units": ALLOWED_ABSENCE_UNITS,
            "absence_boxes_used": ceil(absent_units),
            "percentage": round(present_units / total_units * 100, 2)
            if total_units else 0,
        },
    }


def parse_portal_options(html: str) -> dict[str, list[dict[str, str]]]:
    """Return semester and subject options from an authenticated portal page."""

    soup = BeautifulSoup(html, "html.parser")
    if soup.find("input", {"name": "txtuid"}):
        raise PortalLoginError("The SIBA session is not authenticated.")

    return {
        "semesters": _options(soup, SEMESTER_FIELD),
        "subjects": _options(soup, COURSE_FIELD),
    }


@dataclass
class SibaPortalClient:
    """Small stateful client for the ASP.NET SIBA student portal."""

    base_url: str = "http://sibagrades.iba-suk.edu.pk:86/"
    timeout: float = 20.0

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/") + "/"
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "SIBA Attendance Tracker (local development)"}
        )
        self._attendance_url: str | None = None
        self._page_html: str | None = None

    def _url(self, path: str) -> str:
        return urljoin(self.base_url, path)

    def _get(self, url: str) -> requests.Response:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as error:
            raise PortalError("Could not reach the SIBA portal.") from error
        return response

    def login(self, username: str, password: str) -> None:
        if not username or not password:
            raise PortalLoginError("CMS ID and password are required.")

        login_page = self._get(self._url(LOGIN_PATH))
        soup = BeautifulSoup(login_page.text, "html.parser")
        payload = _hidden_fields(soup)
        payload.update({
            "txtuid": username,
            "txtpwd": password,
            "Button1": "Login",
        })

        try:
            response = self.session.post(
                login_page.url,
                data=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise PortalError("Could not submit the SIBA login form.") from error

        result = BeautifulSoup(response.text, "html.parser")
        if result.find("input", {"name": "txtuid"}):
            message = result.find(id="Label1")
            detail = message.get_text(" ", strip=True) if message else ""
            raise PortalLoginError(detail or "SIBA rejected the credentials.")

        self._attendance_url = self._url(ATTENDANCE_PATH)
        attendance_page = self._get(self._attendance_url)
        self._page_html = attendance_page.text

    def _require_login(self) -> str:
        if not self._page_html:
            raise PortalLoginError("Log in to SIBA before requesting attendance.")
        return self._page_html

    def options(self) -> dict[str, list[dict[str, str | bool]]]:
        return parse_portal_options(self._require_login())

    def select_semester(self, semester: str) -> dict[str, list[dict[str, str | bool]]]:
        """Run SIBA's semester postback and return its refreshed options."""

        if not semester:
            raise PortalResponseError("A semester value is required.")

        soup = BeautifulSoup(self._require_login(), "html.parser")
        payload = _hidden_fields(soup)
        semester_select = soup.find("select", {"name": SEMESTER_FIELD})
        subject_select = soup.find("select", {"name": COURSE_FIELD})
        if not semester_select or not subject_select:
            raise PortalResponseError(
                "SIBA returned a page without semester or subject options."
            )
        subject_option = (
            subject_select.find("option", selected=True)
            or subject_select.find("option")
        )
        if not subject_option:
            raise PortalResponseError("SIBA returned no subject options.")

        payload.update({
            "__EVENTTARGET": SEMESTER_FIELD,
            "__EVENTARGUMENT": "",
            SEMESTER_FIELD: semester,
            COURSE_FIELD: subject_option.get("value", ""),
        })
        try:
            response = self.session.post(
                self._attendance_url or self._url(ATTENDANCE_PATH),
                data=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise PortalError(
                "Could not change the semester on the SIBA portal."
            ) from error

        self._page_html = response.text
        try:
            return parse_portal_options(self._page_html)
        except PortalLoginError:
            raise
        except (ValueError, KeyError) as error:
            raise PortalResponseError(
                "SIBA returned unexpected semester options."
            ) from error

    def attendance(
        self,
        semester: str | None = None,
        subject: str | None = None,
    ) -> dict[str, Any]:
        page_html = self._require_login()
        if semester is not None or subject is not None:
            soup = BeautifulSoup(page_html, "html.parser")
            payload = _hidden_fields(soup)
            semester_select = soup.find("select", {"name": SEMESTER_FIELD})
            subject_select = soup.find("select", {"name": COURSE_FIELD})
            if not semester_select or not subject_select:
                raise PortalResponseError(
                    "SIBA returned a page without semester or subject options."
                )
            semester_option = semester_select.find("option", selected=True)
            subject_option = subject_select.find("option", selected=True)
            if not semester_option:
                semester_option = semester_select.find("option")
            if not subject_option:
                subject_option = subject_select.find("option")
            if not semester_option or not subject_option:
                raise PortalResponseError("SIBA returned empty attendance options.")
            payload.update({
                SEMESTER_FIELD: semester
                or semester_option.get("value", ""),
                COURSE_FIELD: subject
                or subject_option.get("value", ""),
                ATTENDANCE_SUBMIT_FIELD: "CMS CLASS ATTENDANCE",
            })
            try:
                response = self.session.post(
                    self._attendance_url or self._url(ATTENDANCE_PATH),
                    data=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
            except requests.RequestException as error:
                raise PortalError(
                    "Could not request attendance from the SIBA portal."
                ) from error
            page_html = response.text
            self._page_html = page_html

        try:
            return parse_attendance_html(page_html)
        except (ValueError, KeyError) as error:
            raise PortalResponseError(
                "SIBA returned an unexpected attendance page."
            ) from error

    def all_attendance(self, semester_value: str | None = None) -> list[dict[str, Any]]:
        """Fetch attendance summaries for one semester or every semester."""

        semesters = self.options()["semesters"]
        if semester_value:
            semesters = [
                semester for semester in semesters
                if str(semester["value"]) == semester_value
            ]
            if not semesters:
                raise PortalResponseError("The selected semester was not found.")

        snapshots = []
        for semester in semesters:
            semester_value = str(semester["value"])
            options = self.select_semester(semester_value)
            subjects = options["subjects"]
            for subject in subjects:
                subject_value = str(subject["value"])
                result = self.attendance(
                    semester=semester_value,
                    subject=subject_value,
                )
                summary = result["summary"]
                snapshots.append({
                    "semester": result["semester"] or semester,
                    "subject": result["subject"] or subject,
                    "attended": summary["present_units"],
                    "absent": summary["absent_units"],
                    "total": summary["total_units"],
                    "attended_units": summary["present_units"],
                    "absent_units": summary["absent_units"],
                    "total_units": summary["total_units"],
                    "absence_boxes_used": summary["absence_boxes_used"],
                    "allowed_absence_units": summary["allowed_absence_units"],
                    "percentage": summary["percentage"],
                })
        return snapshots
