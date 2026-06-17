import pyhtml
from html import escape

def get_page_html(form_data):
    print("About to return page 2")

    def render_table(headers, rows, image_col=None):
        html = ["<table border='1' cellpadding='6' cellspacing='0' style='border-collapse:collapse;width:100%;'>"]
        html.append("<tr>" + "".join(f"<th>{escape(h)}</th>" for h in headers) + "</tr>")
        for r in rows:
            html.append("<tr>")
            for i, cell in enumerate(r):
                if image_col is not None and i == image_col and isinstance(cell, str) and cell.strip():
                    html.append(f"<td><img src='{escape(cell)}' alt='img' style='max-height:90px'></td>")
                else:
                    html.append(f"<td>{escape(str(cell))}</td>")
            html.append("</tr>")
        html.append("</table>")
        return "".join(html)

    page_html = """<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="static/sub1a.css">
  <meta charset="utf-8">
  <title>Vaccination Insights</title>
</head>
<body>

  <div class="topnav">
    <div class="subtask-links">
       <a href="/">Vacination Data Overview</a>
      <a href="/page2">Vaccination Data</a>
      <a href="/page3">Vaccination Rate</a>
      <a href="/page4">Mission Statement</a>
      <a href="/page5">Infection Data</a>
      <a href="/page6">Infection Rate</a>
    </div>
  </div>

  <div align="left">
    <form action="/page4" method="get" class="search-form">
      <input type="text" name="q" placeholder="Search...">
      <button type="submit">Search</button>
    </form>
  </div>

 <div class="header" style="background-color:#0092c9; color:white; padding:20px; text-align:left;">
  <div style="display:flex; align-items:center;">
    <img src="images/VaxView Logo.png" alt="logo" width="100" height="100" style="margin-right:15px;">
    <h1 style="margin:0; font-size:40px;">VaxView</h1>
  </div>

  <div style="margin-left:115px; margin-top:5px;">
    <h3 style="margin:5px 0;">Welcome to our website</h3>
    <p style="margin:0;">Your reliable source for simple, accurate, and accessible vaccination knowledge.</p>
  </div>
</div>





  <hr>

  <h2><u>How to use:</u></h2>
  <table border="1" cellpadding="8" cellspacing="0" width="100%" style="border-collapse:collapse;">
    <tr>
      <td>Access valid vaccination information</td>
      <td>View vaccination rates by country or region</td>
      <td>View infection rate by economic status</td>
    </tr>
    <tr>
      <td>View countries with largest vaccination improvement</td>
      <td>Analyse improvement trends</td>
      <td>View countries with high infection rates</td>
    </tr>
  </table>
  <hr>

  <h2 style="text-align:center;">Persona Table</h2>
"""

    # Persona table
    persona_rows = pyhtml.get_results_from_query("database/immunisation (1).db", "SELECT * FROM persona;")
    persona_headers = ["Name", "Gender", "Age", "Description", "Needs", "Goals", "Skills", "Image"]
    page_html += render_table(persona_headers, persona_rows, image_col=7)

    # Student details table
    page_html += "<h2 style='text-align:center;margin-top:24px;'>Student Details</h2>"
    student_rows = pyhtml.get_results_from_query("database/immunisation (1).db", "SELECT * FROM student_details;")
    student_headers = ["Name", "Student_ID"]
    page_html += render_table(student_headers, student_rows)

    # Footer
    page_html += """
  <div class="footer">
    <div class="footer-links">
      <a href="/">Home</a>
      <a href="#">About</a>
      <a href="#">Contact</a>
    </div>
    <div class="footer-policy">
      <label for="policy">Policy:</label>
      <select id="policy" name="policy" onchange="location = this.value;">
        <option value="privacy">Privacy Policy</option>
        <option value="terms">Terms of Service</option>
      </select>
    </div>
  </div>

</body>
</html>
"""
    return page_html
