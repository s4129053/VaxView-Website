import pyhtml
import sqlite3
import math

def get_page_html(form_data, current_page="page2"):
    print("About to return page 2")

    # Safely extract filters
    def safe_get(key):
        return form_data.get(key, [''])[0].strip().replace("'", "''") if form_data and key in form_data else ''

    antigen = safe_get('antigen')
    year = safe_get('year')
    region = safe_get('region')
    country = safe_get('country')
    table_page = int(form_data.get("table_page", ["1"])[0]) if form_data else 1

    # Load dropdown options
    db = "database/immunisation (1).db"
    antigen_list = pyhtml.get_results_from_query(db, "SELECT name FROM Antigen;")
    year_list = pyhtml.get_results_from_query(db, "SELECT DISTINCT year FROM Vaccination ORDER BY year DESC;")
    region_list = pyhtml.get_results_from_query(db, "SELECT DISTINCT region FROM Region ORDER BY region;")

    # Country list depends on region
    if region:
        sql = f"""
        SELECT DISTINCT c.name
        FROM Country c
        JOIN Region r ON c.region = r.regionid
        WHERE r.region = '{region}'
        ORDER BY c.name;
        """
        country_list = pyhtml.get_results_from_query(db, sql)
    else:
        country_list = pyhtml.get_results_from_query(db, "SELECT DISTINCT name FROM Country ORDER BY name;")
    # Ensure "All" option is always present at top
    country_list.insert(0, ("All",))

    # Filtered query: countries with ≥90% coverage
    filtered_data = []
    if any([antigen, year, region, country]):
        sql = """
        SELECT a.name, v.year, c.name, r.region, v.coverage
        FROM Vaccination v
        JOIN Antigen a ON v.antigen = a.antigenid
        JOIN Country c ON v.country = c.countryid
        JOIN Region r ON c.region = r.regionid
        WHERE v.coverage >= 90
        """
        if antigen:
            sql += f" AND a.name = '{antigen}'"
        if year:
            sql += f" AND v.year = {int(year)}"
        if region:
            sql += f" AND r.region = '{region}'"
        if country and country != "All":
            sql += f" AND c.name = '{country}'"
        sql += " ORDER BY v.coverage DESC;"

        raw_data = pyhtml.get_results_from_query(db, sql)
        filtered_data = [row for row in raw_data if row[4] not in (None, '', 'NULL')]

    # Pagination (Prev/Next, 5 rows per page)
    rows_per_page = 5
    total_pages = max(1, math.ceil(len(filtered_data) / rows_per_page))
    table_page = max(1, min(table_page, total_pages))
    start = (table_page - 1) * rows_per_page
    end = start + rows_per_page
    table_data = filtered_data[start:end]

    # Region summary query (shown when antigen + year chosen)
    region_summary = []
    if antigen and year:
        region_summary = pyhtml.get_results_from_query(db, f"""
        SELECT a.name, v.year, COUNT(DISTINCT c.name), r.region
        FROM Vaccination v
        JOIN Antigen a ON v.antigen = a.antigenid
        JOIN Country c ON v.country = c.countryid
        JOIN Region r ON c.region = r.regionid
        WHERE a.name = '{antigen}' AND v.year = {int(year)} AND v.coverage >= 90
        GROUP BY r.region;
        """)
            # Navigation links with active class
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
        nav_html += f'<a href="{url}" class="{active_class}">{label}</a> '
    nav_html += '</div></nav>'
    # Build HTML
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Vaccination Data</title>
  <link rel="stylesheet" href="static/sub2a.css?v=2025"/>
</head>

<body>
  {nav_html}

  <form method="get" action="/" class="search-form">
    <input type="text" name="q" placeholder="Search..." />
    <button type="submit">Search</button>
  </form>
  <header class="header">
    <img src="/images/vax.png" class="top-image" alt="Logo" width="100" height="100" />
    <h1>VaxView</h1>
  </header>

  <section class="header2">
    <h2><u><b>Focused view of vaccination data by country and region</b></u></h2>
  </section>

  <main>
    <aside class="filters">
      <h3>Filter By</h3>
      <form method="GET" action="/page2" id="filter-form">
        <label>Antigen:
          <select name="antigen" id="antigen">
            <option value="">Select Antigen</option>"""
    for row in antigen_list:
        name = row[0]
        selected = 'selected' if name == antigen else ''
        page_html += f'<option value="{name}" {selected}>{name}</option>'
    page_html += """</select></label>

        <label>Year:
          <select name="year" id="year">
            <option value="">Select Year</option>"""
    for row in year_list:
        y = str(row[0])
        selected = 'selected' if y == year else ''
        page_html += f'<option value="{y}" {selected}>{y}</option>'
    page_html += """</select></label>

        <label>Region:
          <select name="region" id="region">
            <option value="">Select Region</option>"""
    for row in region_list:
        r = row[0]
        selected = 'selected' if r == region else ''
        page_html += f'<option value="{r}" {selected}>{r}</option>'
    page_html += """</select></label>

        <!-- Apply button moved here -->
        <button type="submit">Apply Filters</button>

        <label>Country:
          <select name="country" id="country">"""
    for row in country_list:
        c = row[0]
        selected = 'selected' if c == country else ''
        page_html += f'<option value="{c}" {selected}>{c}</option>'
    page_html += """</select></label>

        <button type="button" onclick="window.location='/page2'">Clear Filters</button>
      </form>
    </aside>

    <section class="results">
      <div class="table-section">
        <h2>Countries That Met ≥90% Target</h2>
        <table>
          <thead>
            <tr>
              <th>Antigen</th>
              <th>Year</th>
              <th>Country</th>
              <th>Region</th>
              <th>Coverage (%)</th>
            </tr>
          </thead>
          <tbody>"""
    for row in table_data:
        coverage = f"{float(row[4]):.0f}%"
        page_html += f"""<tr>
              <td>{row[0]}</td>
              <td>{row[1]}</td>
              <td>{row[2]}</td>
              <td>{row[3]}</td>
              <td>{coverage}</td>
            </tr>"""
    page_html += """</tbody>
        </table>

        <div class="pagination">"""
    # Prev / Next pagination with filters preserved
    if table_page > 1:
        page_html += f'<a class="prev" href="/page2?table_page={table_page-1}&antigen={antigen}&year={year}&region={region}&country={country}">Prev</a> '
    else:
        page_html += '<span class="prev disabled">Prev</span> '
    if table_page < total_pages:
        page_html += f'<a class="next" href="/page2?table_page={table_page+1}&antigen={antigen}&year={year}&region={region}&country={country}">Next</a>'
    else:
        page_html += '<span class="next disabled">Next</span>'
    page_html += """</div>
      </div>

      <div class="table-section">
        <h2>Region Summary</h2>
        <table>
          <thead>
            <tr>
              <th>Antigen</th>
              <th>Year</th>
              <th>Number of Countries ≥90%</th>
              <th>Region</th>
            </tr>
          </thead>
          <tbody>"""
    for row in region_summary:
        page_html += f"""<tr>
              <td>{row[0]}</td>
              <td>{row[1]}</td>
              <td>{row[2]}</td>
              <td>{row[3]}</td>
            </tr>"""
    page_html += """</tbody>
        </table>
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="footer-links">
      <a href="/">Home</a>
      <a href="#">About</a>
      <a href="#">Contact</a>
    </div>
    <div class="footer-policy">
      <label for="policy">Policy:</label>
      <select id="policy" name="policy" onchange="location = this.value;">
        <option value="#">Privacy Policy</option>
        <option value="#">Terms of Service</option>
      </select>
    </div>
  </footer>

  <script>
    // Optional UX improvement: when region changes, reset country selection
    document.addEventListener("DOMContentLoaded", function () {
      const regionSelect = document.getElementById("region");
      const countrySelect = document.getElementById("country");
      regionSelect.addEventListener("change", () => {
        countrySelect.selectedIndex = 0; // reset to first option (All)
      });
    });
  </script>

</body>
</html>
"""
    return page_html