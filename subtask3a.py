import pyhtml
import math

def get_page_html(form_data):
    db_path = "database/immunisation (1).db"

    # Fetch dropdown data
    antigens = pyhtml.get_results_from_query(db_path, "SELECT DISTINCT AntigenID FROM Antigen;")
    years = [row[0] for row in pyhtml.get_results_from_query(db_path, "SELECT DISTINCT YearID FROM YearDate ORDER BY YearID;")]

    # Extract selected filters safely
    selected_antigen = form_data.get("antigen", [""])[0]
    selected_start_year = form_data.get("start_year", [""])[0]
    selected_end_year = form_data.get("end_year", [""])[0]
    selected_n = form_data.get("num_countries", [""])[0]
    table_page = int(form_data.get("page", ["1"])[0]) if form_data else 1

    # Build dropdown options
    antigen_options = "".join(
        f"<option value='{antigen}' {'selected' if selected_antigen == str(antigen) else ''}>{antigen}</option>"
        for (antigen,) in antigens
    )
    start_year_options = "".join(
        f"<option value='{year}' {'selected' if selected_start_year == str(year) else ''}>{year}</option>"
        for year in years
    )
    end_year_options = "".join(
        f"<option value='{year}' {'selected' if selected_end_year == str(year) else ''}>{year}</option>"
        for year in years if not selected_start_year or int(year) >= int(selected_start_year)
    )

    # Query results
    results = []
    row_count = 0
    if selected_antigen and selected_start_year and selected_end_year and selected_n.isdigit():
        start_year = int(selected_start_year)
        end_year = int(selected_end_year)
        antigen = selected_antigen.replace("'", "''")
        limit = int(selected_n)

        sql = f"""
            SELECT v1.country,
                   ROUND(v2.coverage - v1.coverage, 2) AS VaccinationRateIncrease,
                   v1.year AS StartYear,
                   v2.year AS EndYear
            FROM Vaccination v1
            JOIN Vaccination v2 ON v1.country = v2.country AND v1.antigen = v2.antigen
            WHERE v1.year = {start_year} AND v2.year = {end_year} AND v1.antigen = '{antigen}'
            ORDER BY VaccinationRateIncrease DESC
            LIMIT {limit}
        """
        results = pyhtml.get_results_from_query(db_path, sql)
        row_count = len(results)

    # Pagination setup
    rows_per_page = 5
    total_pages = max(1, math.ceil(row_count / rows_per_page))
    table_page = max(1, min(table_page, total_pages))
    start = (table_page - 1) * rows_per_page
    end = start + rows_per_page
    paginated_results = results[start:end]

    # Build results table with serial numbers
    results_html = ""
    for idx, (country, rate, start_y, end_y) in enumerate(paginated_results, start=start+1):
        results_html += f"<tr><td>{idx}</td><td>{country}</td><td>{rate}</td><td>{start_y}</td><td>{end_y}</td></tr>"

    # Navbar
    current_page = "page3"
    nav_links = {
        "overview": ("/", "Vaccination Data Overview"),
        "page2": ("/page2", "Vaccination Data"),
        "page3": ("/page3", "Vaccination Rate"),
        "page4": ("/page4", "Mission Statement"),
        "page5": ("/page5", "Infection Data"),
        "page6": ("/page6", "Infection Rate")
    }
    nav_html = '<nav class="topnav"><div class="subtask-links">'
    for key, (url, label) in nav_links.items():
        active_class = "active" if key == current_page else ""
        nav_html += f'<a href="{url}" class="{active_class}">{label}</a>'
    nav_html += '</div></nav>'

    # Pagination HTML
    pagination_html = '<div class="pagination">'
    if table_page > 1:
        pagination_html += f'<a href="/page3?page={table_page-1}&antigen={selected_antigen}&start_year={selected_start_year}&end_year={selected_end_year}&num_countries={selected_n}">Prev</a> '
    else:
        pagination_html += '<span class="disabled">Prev</span> '

    for i in range(1, total_pages+1):
        active = "class=\'active-page\'" if i == table_page else ""
        pagination_html += f'<a href="/page3?page={i}&antigen={selected_antigen}&start_year={selected_start_year}&end_year={selected_end_year}&num_countries={selected_n}" {active}>{i}</a> '

    if total_pages > 1 and table_page < total_pages:
        pagination_html += f'<a href="/page3?page={table_page+1}&antigen={selected_antigen}&start_year={selected_start_year}&end_year={selected_end_year}&num_countries={selected_n}">Next</a>'
    else:
        pagination_html += '<span class="disabled">Next</span>'
    pagination_html += '</div>'

    # Final HTML
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Vaccination Rate Analysis</title>
  <link rel="stylesheet" href="static/sub3a.css" />
</head>
<body>
  {nav_html}

  <header class="header">
    <img src="/images/vax.png" class="top-image" alt="Logo" width="100" height="100" />
    <h1>VaxView</h1>
  </header>

  <section class="header2"><h2><u>Filter Criteria</u></h2></section>
  <aside class="filters">
  <h3>Filter By</h3>
  <form method="get" action="/page3" id="filter-form" class="filter-form">

    <div class="filter-group">
      <label for="antigen">Antigen:</label>
      <select name="antigen" id="antigen" required>
        <option value="">Select Antigen</option>
        {antigen_options}
      </select>
    </div>

    <div class="filter-group">
      <label for="start_year">Start Year:</label>
      <select name="start_year" id="start_year" required>
        <option value="">Select Start Year</option>
        {start_year_options}
      </select>
    </div>

    <div class="filter-group">
      <label for="end_year">End Year:</label>
      <select name="end_year" id="end_year" required>
        <option value="">Select End Year</option>
        {end_year_options}
      </select>
    </div>

    <div class="filter-group">
      <label for="num_countries">Number of Countries:</label>
      <input type="number" name="num_countries" id="num_countries"
             value="{selected_n or ''}" min="1" placeholder="e.g. 10" required />
    </div>

    <div class="filter-actions">
      <button type="submit" class="btn-primary">Apply Filters</button>
      <button type="button" class="btn-secondary" onclick="window.location='/page3'">Clear Filters</button>
    </div>
  </form>
</aside>

  <section class="header2"><h2><u>Search Results</u></h2></section>
  <section class="results">
    <p><strong>Showing {row_count} countries</strong></p>
    <table>
      <tr><th>Serial No</th><th>Country</th><th>Vaccination Rate Increase</th><th>Start Year</th><th>End Year</th></tr>
      {results_html}
    </table>
    {pagination_html}
  </section>

  <footer class="footer">
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
  </footer>
  
</body>
</html>"""
