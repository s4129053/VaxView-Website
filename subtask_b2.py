import pyhtml
from html import escape

def get_page_html(form_data):
    # get selected filter values safely
    sel_disease = str(form_data.get("disease", "")).strip("[]'")
    sel_year = str(form_data.get("year", "")).strip("[]'")
    sel_econ = str(form_data.get("econ_phase", "")).strip("[]'")

    db = "database/immunisation (1).db"

    # start HTML
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

<form method="get" action="/page5">
  <h3>Data Filters</h3>
"""

    # get disease list
    diseases = [r[0] for r in pyhtml.get_results_from_query(db, "SELECT description FROM infection_type;")]
    page_html += "<b>Preventable Disease:</b><br>"
    for d in diseases:
        checked = "checked" if d == sel_disease else ""
        page_html += f"<input type='radio' name='disease' value='{escape(d)}' {checked}> {escape(d)}<br>"
    page_html += "<br>"

    # year field
    page_html += (
        f"<b>Year:</b><br>"
        f"<input type='text' name='year' value='{escape(sel_year)}' placeholder='2000-2025'><br><br>"
    )

    # get economic phases
    econph = [r[0] for r in pyhtml.get_results_from_query(db, "SELECT phase FROM Economy;")]
    page_html += "<details><summary><b>Advanced Filter</b></summary><b>Economic Phase:</b><br>"
    for e in econph:
        checked = "checked" if e == sel_econ else ""
        page_html += f"<input type='radio' name='econ_phase' value='{escape(e)}' {checked}> {escape(e)}<br>"
    page_html += "</details><br>"

    page_html += "<button type='submit'>Apply Filter</button></form><hr>"

    # ---- query logic ----
    results, headers = [], []

    # disease + year, no econ filter
    if sel_disease and sel_year and not sel_econ:
        sql = f"""
        SELECT C.name AS Country, IT.year, E.phase AS Economic_Phase, IT.cases
        FROM Infectiondata IT
        JOIN Country C ON IT.country = C.CountryID
        JOIN Economy E ON C.economy = E.economyID
        JOIN Infection_type T ON IT.inf_type = T.id
        WHERE lower(T.description) = lower('{sel_disease}')
          AND IT.year = {sel_year};
        """
        headers = ["Country", "Year", "Economic_Phase", "Cases"]
        results = pyhtml.get_results_from_query(db, sql)

    # disease + year + econ filter
    elif sel_disease and sel_year and sel_econ:
        sql = f"""
        SELECT T.description AS Disease, C.name, E.phase, I.year,
               (I.cases * 100000.0 / CP.population) AS Cases_per_100000
        FROM Infectiondata I
        JOIN Infection_type T ON I.inf_type = T.id
        JOIN Country C ON I.country = C.CountryID
        JOIN Economy E ON C.economy = E.economyID
        JOIN Countrypopulation CP ON C.CountryID = CP.country AND I.year = CP.year
        WHERE lower(T.description) = lower('{sel_disease}')
          AND lower(E.phase) = lower('{sel_econ}')
          AND I.year = {sel_year}
          AND I.cases > 0;
        """
        headers = ["Disease", "Country", "Economic_Phase", "Year", "Cases_per_100000"]
        results = pyhtml.get_results_from_query(db, sql)

    # ---- display results ----
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
</body>
</html>
"""

    return page_html
