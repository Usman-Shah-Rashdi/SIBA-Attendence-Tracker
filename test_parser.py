
from siba_portal import parse_attendance_html

sample_html = """
<html>
<body>
<select name="ctl00$ContentPlaceHolder1$Dpsemester">
    <option selected="selected" value="2613">Fall 2026</option>
</select>

<select name="ctl00$ContentPlaceHolder1$DpCmscourses">
    <option selected="selected" value="1328">Linear Algebra</option>
</select>

<table id="ctl00_ContentPlaceHolder1_RadGrid1_ctl00">
    <thead>
        <tr>
            <th>S.no</th>
            <th>Attendacne Date</th>
            <th>From Time</th>
            <th>Present</th>
            <th>Class Minutes</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td>16-OCT-2026</td>
            <td>09:00</td>
            <td>Present</td>
            <td>100</td>
        </tr>
        <tr>
            <td>2</td>
            <td>02-OCT-2026</td>
            <td>11:10</td>
            <td>Absent</td>
            <td>50</td>
        </tr>
    </tbody>
</table>
</body>
</html>
"""

result = parse_attendance_html(sample_html)

assert result["semester"]["name"] == "Fall 2026"
assert result["subject"]["name"] == "Linear Algebra"
assert result["summary"]["present"] == 1
assert result["summary"]["absent"] == 1
assert result["summary"]["present_units"] == 2.0
assert result["summary"]["absent_units"] == 1.0
assert result["summary"]["total_units"] == 3.0
assert result["summary"]["percentage"] == 66.67

print("Parser test passed!")
print(result)
