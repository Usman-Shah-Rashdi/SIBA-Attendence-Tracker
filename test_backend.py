import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from siba_portal import SibaPortalClient
from app import app


PROJECT_ROOT = Path(__file__).parent
ATTENDANCE_HTML = (PROJECT_ROOT / "actual_attendance.html").read_text(
    encoding="utf-8"
)
LOGIN_HTML = """
<form id="form1">
  <input type="hidden" name="__VIEWSTATE" value="state">
  <input name="txtuid" type="text">
  <input name="txtpwd" type="password">
</form>
"""


class FakeResponse:
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def raise_for_status(self):
        return None


class FakeSession:
    def __init__(self):
        self.headers = {}
        self.posts = []
        self.get_count = 0

    def get(self, url, timeout):
        self.get_count += 1
        html = LOGIN_HTML if self.get_count == 1 else ATTENDANCE_HTML
        return FakeResponse(html, url)

    def post(self, url, data, timeout):
        self.posts.append((url, data))
        return FakeResponse(ATTENDANCE_HTML, url)


class SibaPortalClientTests(unittest.TestCase):
    def setUp(self):
        self.client = SibaPortalClient(base_url="http://portal.test/")
        self.session = FakeSession()
        self.client.session = self.session

    def test_login_loads_options_and_attendance(self):
        self.client.login("cms-id", "secret")

        options = self.client.options()
        result = self.client.attendance()

        self.assertEqual(options["semesters"][0]["name"], "Fall 2026")
        self.assertEqual(options["subjects"][0]["name"], "Linear Algebra")
        self.assertEqual(result["summary"]["present_units"], 17.2)
        self.assertEqual(result["summary"]["absent_units"], 7.0)
        self.assertEqual(result["summary"]["total_units"], 24.2)
        self.assertEqual(result["summary"]["absence_boxes_used"], 7)
        self.assertEqual(result["summary"]["percentage"], 71.07)
        self.assertEqual(len(self.session.posts), 1)
        self.assertEqual(self.session.posts[0][1]["txtuid"], "cms-id")

    def test_attendance_selection_posts_aspnet_form(self):
        self.client.login("cms-id", "secret")
        self.client.attendance(semester="2612", subject="1321")

        payload = self.session.posts[-1][1]
        self.assertEqual(payload["ctl00$ContentPlaceHolder1$Dpsemester"], "2612")
        self.assertEqual(payload["ctl00$ContentPlaceHolder1$DpCmscourses"], "1321")
        self.assertEqual(
            payload["ctl00$ContentPlaceHolder1$Button1"],
            "CMS CLASS ATTENDANCE",
        )

    def test_semester_change_posts_aspnet_event_and_refreshes_options(self):
        self.client.login("cms-id", "secret")
        options = self.client.select_semester("2612")

        payload = self.session.posts[-1][1]
        self.assertEqual(payload["__EVENTTARGET"], "ctl00$ContentPlaceHolder1$Dpsemester")
        self.assertEqual(payload["ctl00$ContentPlaceHolder1$Dpsemester"], "2612")
        self.assertEqual(options["subjects"][0]["name"], "Linear Algebra")

    def test_all_attendance_returns_snapshot_records(self):
        self.client.login("cms-id", "secret")
        snapshots = self.client.all_attendance()

        self.assertEqual(len(snapshots), 70)
        self.assertEqual(snapshots[0]["semester"]["name"], "Fall 2026")
        self.assertEqual(snapshots[0]["subject"]["name"], "Linear Algebra")
        self.assertEqual(snapshots[0]["attended"], 17.2)
        self.assertEqual(snapshots[0]["total"], 24.2)
        self.assertEqual(snapshots[0]["absence_boxes_used"], 7)

    def test_all_attendance_can_limit_to_one_semester(self):
        self.client.login("cms-id", "secret")
        snapshots = self.client.all_attendance("2613")

        self.assertEqual(len(snapshots), 10)
        self.assertTrue(all(item["semester"]["value"] == "2613" for item in snapshots))

    def test_snapshot_route_passes_selected_semester(self):
        fake_client = Mock()
        fake_client.all_attendance.return_value = [{"semester": {"value": "2613"}}]
        with app.test_client() as flask_client:
            with patch("app._client", return_value=fake_client):
                response = flask_client.get("/api/attendance/snapshot?semester=2613")

        self.assertEqual(response.status_code, 200)
        fake_client.all_attendance.assert_called_once_with(semester_value="2613")

    def test_snapshot_route_rejects_empty_semester(self):
        with app.test_client() as flask_client:
            response = flask_client.get("/api/attendance/snapshot?semester=")

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
