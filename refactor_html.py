import os
from bs4 import BeautifulSoup

file_path = "c:/Users/essad/Downloads/project 1/marketmind/templates/index.html"
with open(file_path, "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# 1. Create the new wrapper structure
app_layout = soup.new_tag("div", **{"class": "app-layout"})
sidebar = soup.new_tag("aside", **{"class": "app-sidebar"})
main_wrapper = soup.new_tag("div", **{"class": "main-content-wrapper"})
content_area = soup.new_tag("main", **{"class": "content-area"})

# 2. Build Sidebar Navigation
sidebar.append(BeautifulSoup("""
    <div class="sidebar-brand">
        <i class="fas fa-chart-line"></i>
        <span>MarketMind</span>
    </div>
    <nav class="sidebar-nav" id="sidebarNav">
        <a href="#home" class="sidebar-link active" data-view="view-home">
            <i class="fas fa-home"></i> <span>Home</span>
        </a>
        <a href="#dashboard" class="sidebar-link" data-view="view-dashboard">
            <i class="fas fa-chart-pie"></i> <span>Dashboard</span>
        </a>
        <a href="#campaign" class="sidebar-link" data-view="view-campaign">
            <i class="fas fa-bullseye"></i> <span>Campaign Gen</span>
        </a>
        <a href="#pitch" class="sidebar-link" data-view="view-pitch">
            <i class="fas fa-handshake"></i> <span>Pitch Creator</span>
        </a>
        <a href="#lead" class="sidebar-link" data-view="view-lead">
            <i class="fas fa-chart-bar"></i> <span>Lead Qualifier</span>
        </a>
    </nav>
""", "html.parser"))

app_layout.append(sidebar)

# 3. Find and adapt the Top Navbar
old_nav = soup.find("header", {"id": "navbar"})
if old_nav:
    # Remove branding and nav-links from top bar
    brand = old_nav.find("a", {"class": "nav-brand"})
    if brand: brand.extract()
    links = old_nav.find("nav", {"id": "navLinks"})
    if links: links.extract()
    
    old_nav['class'] = "top-navbar"
    main_wrapper.append(old_nav.extract())

# 4. Extract and Group Sections into Views
view_home = soup.new_tag("div", id="view-home", **{"class": "view-section active"})
view_dashboard = soup.new_tag("div", id="view-dashboard", **{"class": "view-section"})
view_campaign = soup.new_tag("div", id="view-campaign", **{"class": "view-section"})
view_pitch = soup.new_tag("div", id="view-pitch", **{"class": "view-section"})
view_lead = soup.new_tag("div", id="view-lead", **{"class": "view-section"})

# Mapping elements to their respective views
sec_home = soup.find("section", {"id": "home"})
if sec_home: view_home.append(sec_home.extract())

sec_features = soup.find("section", {"id": "features"})
if sec_features: view_home.append(sec_features.extract())

sec_platforms = soup.find("section", {"id": "platforms"})
if sec_platforms: view_home.append(sec_platforms.extract())

sec_dash = soup.find("section", {"id": "dashboard"})
if sec_dash: view_dashboard.append(sec_dash.extract())

sec_camp = soup.find("section", {"id": "campaign"})
if sec_camp: view_campaign.append(sec_camp.extract())

sec_pitch = soup.find("section", {"id": "pitch"})
if sec_pitch: view_pitch.append(sec_pitch.extract())

sec_lead = soup.find("section", {"id": "lead"})
if sec_lead: view_lead.append(sec_lead.extract())

# Add views to content area
content_area.append(view_home)
content_area.append(view_dashboard)
content_area.append(view_campaign)
content_area.append(view_pitch)
content_area.append(view_lead)

# Add footer to content area
footer = soup.find("footer", {"class": "footer"})
if footer:
    content_area.append(footer.extract())

main_wrapper.append(content_area)
app_layout.append(main_wrapper)

# Insert the layout into the body right after where the old nav used to be effectively
# Since we extracted a lot, we will insert app_layout at the beginning of the body
body = soup.find("body")
body.insert(0, app_layout)

# Save the modified HTML
with open(file_path, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("DOM restructuring complete!")
