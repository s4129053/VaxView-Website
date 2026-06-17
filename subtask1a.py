import pyhtml
import sqlite3

def get_page_html(form_data, current_page="overview"):
    print("About to return page 2")

    db_path = "database/immunisation (1).db"

    # SQL queries
    sql_timeframe = "SELECT Min(YearID), Max(YearID) FROM YearDate;"
    sql_disease_count = "SELECT COUNT(DISTINCT id) FROM Infection_Type;"
    sql_infections = "SELECT id, description FROM Infection_Type ORDER BY description;"

    # Query results
    start, end = pyhtml.get_results_from_query(db_path, sql_timeframe)[0]
    total_diseases = pyhtml.get_results_from_query(db_path, sql_disease_count)[0][0]
    total_vaccines = pyhtml.get_results_from_query(db_path, sql_disease_count)[0][0]  # Placeholder
    infections = pyhtml.get_results_from_query(db_path, sql_infections)

    # Build infection list HTML
    infection_list_html = "<ul class='infections-list'>"
    for code, name in infections:
        infection_list_html += f"<li><span class='code'>{code}</span>: {name}</li>"
    infection_list_html += "</ul>"

    # Dropdown cards
    dropdown_cards_html = ""
    subtasks = [
        ("What does Vaccination Data Overview page do?", "It shows the database timeframe, infection types, and vaccine coverage. Also Shows highlited topics of this website"),
        ("What does Vaccination Data page do?", "It lets you filter vaccination data by antigen, year, and country."),
        ("What does Vaccination Rate page do?", "It compares vaccination rate increases across countries and timeframes."),
        ("What does Mission Statement page do?", "It analyzes regional vaccination trends and economic phase correlations."),
        ("What does Infection Data page do?", "It visualizes vaccination data with interactive graphs and summaries."),
        ("What does Infection Rate page do?", "It exports filtered results and integrates policy dropdowns.")
    ]

    for label, summary in subtasks:
        dropdown_cards_html += f"""
        <div class="card dropdown-card">
          <div class="container">
            <button class="dropdown-btn">
              <span class="btn-label">{label}</span>
              <span class="arrow">&#9662;</span>
            </button>
            <div class="dropdown-content">
              <p>{summary}</p>
            </div>
          </div>
        </div>
        """

    # Navigation links with active class
    nav_links = {
        "overview": "/",
        "page2": "/page2",
        "page3": "/page3",
        "page4": "/page4",
        "page5": "/page5",
        "page6": "/page6"
    }

    nav_html = '<nav class="topnav"><div class="subtask-links">'
    for key, url in nav_links.items():
        label = {
            "overview": "Vaccination Data Overview",
            "page2": "Vaccination Data",
            "page3": "Vaccination Rate",
            "page4": "Mission Statement",
            "page5": "Infection Data",
            "page6": "Infection Rate"
        }[key]
        active_class = "active" if key == current_page else ""
        nav_html += f'<a href="{url}" class="{active_class}">{label}</a>'
    nav_html += '</div></nav>'

    # Final HTML
    page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Vaccination Data Overview</title>
  <link rel="stylesheet" href="static/sub1a.css" />
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
    <h2><u>Data Overview</u></h2>
  </section>

  <section class="overview">
    <div class="data-description">
      <h3>Covered Database Timeframe</h3>
      <p class="big">{start} - {end}</p>
    </div>
    <div class="data-description">
      <h3>Total Preventable Diseases</h3>
      <p class="big">{total_diseases}</p>
    </div>
    <div class="data-description">
      <h3>Infection Diseases Name</h3>
      <div class="infections-list">{infection_list_html}</div>
    </div>
    <div class="data-description">
      <h3>Total Administered Vaccines</h3>
      <p class="big">{total_vaccines}</p>
    </div>
  </section>

  <section class="header2">
    <h2><u>Highlighted Topics</u></h2>
  </section>

  <section class="cards">
    {dropdown_cards_html}
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

  <script>
    document.addEventListener("DOMContentLoaded", function() {{
      const buttons = document.querySelectorAll(".dropdown-btn");

      buttons.forEach(function(btn) {{
        const content = btn.parentElement.querySelector(".dropdown-content");
        btn.classList.remove("active");
        content.style.display = "none";

        btn.addEventListener("click", function() {{
          const isOpen = btn.classList.contains("active");
          btn.classList.toggle("active");
          content.style.display = isOpen ? "none" : "block";
        }});
      }});
    }});
  </script>

</body>
</html>
"""
    return page_html