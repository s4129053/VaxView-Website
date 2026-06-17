import pyhtml
from html import escape

def get_page_html(form_data):
    sel_disease = str(form_data.get("disease", "")).strip("[]'").lower()
    sel_year = str(form_data.get("year", "")).strip("[]'")

    db = "database/immunisation (1).db"

    page_html = """<!DOCTYPE html>
<html>
<head>
<title>Vaccination Data Filters</title>
<meta charset="utf-8">
<link rel="stylesheet" href="static/sub1a.css">
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
</div>

<hr>

<form method="get" action="/page6">
  <h3>Data Filters</h3>
"""

    # diseases
    diseases = [r[0] for r in pyhtml.get_results_from_query(db, "SELECT description FROM infection_type;")]
    page_html += "<b>Preventable Disease:</b><br>"
    for d in diseases:
        checked = "checked" if d.lower() == sel_disease else ""
        page_html += f"<input type='radio' name='disease' value='{escape(d)}' {checked}> {escape(d)}<br>"
    page_html += "<br>"

    # year
    page_html += (
        f"<b>Year:</b><br>"
        f"<input type='text' name='year' value='{escape(sel_year)}' placeholder='2000-2025'><br><br>"
    )

    page_html += "<button type='submit'>Apply Filter</button></form><hr>"

    # query
    results, headers = [], []
    if sel_disease and sel_year:
        sql = f"""
WITH Infection_rate AS (
  SELECT
    IT.description AS preventable_disease,
    C.name AS Country,
    (I.cases * 100000.0 / CP.population) AS Cases_per_100000_people,
    I.year
  FROM Infectiondata AS I
  INNER JOIN Infection_type AS IT ON I.inf_type = IT.id
  INNER JOIN Country AS C ON C.CountryID = I.country
  INNER JOIN Countrypopulation AS CP ON C.CountryID = CP.country AND I.year = CP.year
  WHERE lower(IT.description) = '{sel_disease}'
    AND I.cases > 0
    AND I.year = '{sel_year}'
),
Global_avg AS (
  SELECT preventable_disease, Country, Cases_per_100000_people, year FROM Infection_rate
  UNION ALL
  SELECT preventable_disease,
         'Global' AS Country,
         AVG(Cases_per_100000_people) AS Cases_per_100000_people,
         year
  FROM Infection_rate
  GROUP BY year, preventable_disease
)
SELECT *
FROM Global_avg
ORDER BY
  CASE WHEN Country = 'Global' THEN 0 ELSE 1 END,
  Cases_per_100000_people DESC;
"""
        headers = ["Preventable_disease", "Country", "Cases_per_100000", "Year"]
        results = pyhtml.get_results_from_query(db, sql)

    # results
    if results:
        page_html += "<h3>Results</h3><table border='1' cellpadding='6'>"
        page_html += "<tr>" + "".join(f"<th>{escape(str(h))}</th>" for h in headers) + "</tr>"
        for row in results:
            page_html += "<tr>" + "".join(f"<td>{escape(str(x))}</td>" for x in row) + "</tr>"
        page_html += "</table>"
    else:
        page_html += "<p>No results found. Please select filters and try again.</p>"

    # footer
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
</body></html>"""

    return page_html
