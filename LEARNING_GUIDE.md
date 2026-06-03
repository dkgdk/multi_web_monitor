# 📚 Multi Web Monitor — Step-by-Step Learning Guide

Welcome! This guide walks you through the entire project in a logical learning order.
Read each section, then open the referenced file and study the code.

---

## 🗂 Project Structure Overview

```
multi_web_monitor/
├── manage.py                      # Django entry point
├── multi_web_monitor/             # Project configuration
│   ├── settings.py                # All Django settings
│   ├── urls.py                    # Root URL routing
│   ├── celery.py                  # Background task engine
│   └── __init__.py                # Loads Celery on startup
├── monitors/                      # Main app (core logic)
│   ├── models.py                  # Database tables
│   ├── views.py                   # Page logic (controllers)
│   ├── urls.py                    # App URL routing
│   ├── forms.py                   # Django forms
│   ├── admin.py                   # Admin panel config
│   ├── checker.py                 # Website checking utility
│   └── tasks.py                   # Celery background tasks
├── api/                           # REST API app
│   ├── serializers.py             # JSON conversion
│   ├── views.py                   # API endpoints
│   └── urls.py                    # API URL routing
├── templates/monitors/            # HTML templates
│   ├── base.html                  # Layout template
│   ├── dashboard.html             # Main dashboard
│   ├── website_detail.html        # Site detail page
│   ├── website_form.html          # Add/Edit form
│   └── incidents.html             # Incidents page
└── static/                        # CSS, JS, images
    ├── css/style.css
    ├── js/main.js
    └── img/globe.svg
```

---

## Step 1: Django Project Configuration

**File:** `multi_web_monitor/settings.py`

Start here — this is the brain of the project. Learn:

- `INSTALLED_APPS` — What apps are loaded (monitors, api, rest_framework, crispy_forms)
- `DATABASES` — We use SQLite (simple file-based database)
- `TEMPLATES` — Where Django finds HTML files
- `STATIC_URL` / `STATICFILES_DIRS` — Where CSS/JS lives
- `CELERY_*` — Background task settings (uses Redis)
- `REST_FRAMEWORK` — API configuration

**Key concept:** Django projects have a "project config" folder (multi_web_monitor/) and one or more "apps" (monitors/, api/).

---

## Step 2: Models (Database Design)

**File:** `monitors/models.py`

This is the most important file. It defines your database tables:

### Website model
- Stores each monitored site: name, url, check_interval, timeout
- Tracks live state: current_status (up/down/unknown), response_time, uptime_percentage
- Has helper methods like `update_uptime()` and properties like `status_color`

### MonitorCheck model
- One record per check attempt
- ForeignKey to Website (many checks → one website)
- Stores: status, response_time, status_code, error_message, checked_at

### Incident model
- Created automatically when a site goes DOWN
- Resolved automatically when it comes back UP
- Has severity levels: critical, warning, info

**Key concepts:**
- `models.CharField`, `models.URLField`, `models.ForeignKey`
- `auto_now_add=True` vs `auto_now=True` (created vs updated timestamps)
- `related_name='checks'` lets you do `website.checks.all()`
- `class Meta: ordering = ['-created_at']` — default sort order

---

## Step 3: The Website Checker

**File:** `monitors/checker.py`

This is the utility that actually pings websites:

- `check_website(website)` — Makes an HTTP GET request using `httpx`
- Measures response time in milliseconds
- Returns a dict: `{status, response_time, status_code, error_message}`
- Handles timeouts, connection errors, and unexpected errors

- `run_check_for_website(website)` — The full pipeline:
  1. Calls `check_website()` to ping the site
  2. Creates a `MonitorCheck` record in the database
  3. Updates the Website's stats (total_checks, uptime_percentage)
  4. Auto-creates an `Incident` if site just went down
  5. Auto-resolves incidents if site came back up

**Key concepts:**
- `httpx` library for HTTP requests (modern alternative to `requests`)
- `time.monotonic()` for accurate timing
- Separation of concerns: checker logic is separate from views

---

## Step 4: Django Forms

**File:** `monitors/forms.py`

- `WebsiteForm` is a `ModelForm` — it auto-generates form fields from the Website model
- `Meta.fields` controls which fields appear in the form
- `widgets` dict customizes each field's HTML (adds CSS classes, placeholders)
- `labels` dict provides user-friendly field names

**Key concept:** ModelForms save you from writing HTML form fields manually. Django handles validation too.

---

## Step 5: Views (Controller Logic)

**File:** `monitors/views.py`

Views are functions that handle HTTP requests and return responses:

### `dashboard(request)`
- Queries all websites, counts up/down/unknown
- Gets recent incidents and checks
- Calculates average response time
- Passes everything to the template as `context`

### `website_detail(request, pk)`
- Gets one website by its primary key (pk)
- Loads 24h check history for the chart
- Loads last 50 checks for the table

### `website_add(request)` / `website_edit(request, pk)`
- GET → show empty/prefilled form
- POST → validate and save form, then redirect

### `website_delete(request, pk)` / `website_check_now(request, pk)`
- POST-only views (using `@require_POST` decorator)
- `check_now` returns JSON for AJAX calls

### `api_status(request)`
- Returns all website statuses as JSON (used by dashboard auto-refresh)

**Key concepts:**
- `get_object_or_404()` — returns 404 if object doesn't exist
- `request.method == 'POST'` — distinguishes form submission from page load
- `JsonResponse` — returns JSON instead of HTML
- `messages.success()` — flash messages shown after redirect
- `select_related('website')` — optimizes database queries (prevents N+1)

---

## Step 6: URL Routing

**Files:** `multi_web_monitor/urls.py` and `monitors/urls.py`

### Root URLs (multi_web_monitor/urls.py)
```python
path('admin/', admin.site.urls),       # Django admin
path('', include('monitors.urls')),    # Main app at root /
path('api/v1/', include('api.urls')),  # REST API at /api/v1/
```

### App URLs (monitors/urls.py)
```python
path('', views.dashboard)                        # /
path('websites/add/', views.website_add)          # /websites/add/
path('websites/<int:pk>/', views.website_detail)  # /websites/1/
path('websites/<int:pk>/check/', ...)             # /websites/1/check/
```

**Key concepts:**
- `app_name = 'monitors'` enables namespaced URLs: `{% url 'monitors:dashboard' %}`
- `<int:pk>` captures a number from the URL and passes it to the view
- `include()` delegates URL matching to another file

---

## Step 7: Templates (HTML)

### base.html — The Layout
- Every page extends this template
- Contains: sidebar navigation, top bar, messages, content area
- Uses `{% block content %}{% endblock %}` for page-specific content
- Loads CSS, JS, Bootstrap, Chart.js

### dashboard.html — Main Dashboard
- Stats grid (total, online, offline, uptime, response)
- Active incidents banner
- Monitor cards with status, uptime bar, actions
- Recent activity table
- Auto-refresh JavaScript (fetches API every 30s)

### website_detail.html — Site Details
- Header card with site info and big status badge
- Stats row (uptime, response, checks, 24h uptime, interval)
- Chart.js line chart for response time
- Incidents list
- Check history table

### website_form.html — Add/Edit Form
- Renders Django form fields with custom layout
- Two-column and three-column grid layouts
- Toggle switch for active monitoring

### incidents.html — All Incidents
- Open incidents with severity icons
- Resolved incidents (dimmed)

**Key concepts:**
- `{% extends 'monitors/base.html' %}` — template inheritance
- `{% block content %}...{% endblock %}` — overrides parent blocks
- `{{ website.name }}` — outputs a variable
- `{% for item in list %}...{% endfor %}` — loops
- `{% if condition %}...{% endif %}` — conditionals
- `{% url 'monitors:dashboard' %}` — generates URLs by name
- `{{ check.checked_at|timesince }}` — template filters
- `{% csrf_token %}` — security token required for POST forms
- `{% load static %}` — enables `{% static 'css/style.css' %}`

---

## Step 8: Static Files (CSS & JS)

### static/css/style.css
- Complete dark theme using CSS custom properties (variables)
- Glassmorphism effects, gradient accents
- Responsive grid layouts
- Component-specific styles (cards, tables, badges, forms)
- Animations (pulse, spin, slideIn)

### static/js/main.js
- `toggleSidebar()` — show/hide mobile sidebar
- `updateClock()` — live time in the top bar
- `checkNow()` — AJAX POST to check a website without page reload
- `getCookie()` — reads CSRF token from cookies
- Auto-dismiss toasts after 4 seconds

**Key concepts:**
- CSS custom properties: `--accent: #6366f1;` used everywhere
- `fetch()` API for AJAX calls
- CSRF token handling for Django POST requests
- `@media (max-width: 768px)` — mobile responsive breakpoints

---

## Step 9: Django Admin

**File:** `monitors/admin.py`

- `@admin.register(Website)` — registers model with admin
- `list_display` — columns shown in the list view
- `list_filter` — sidebar filters
- `search_fields` — enables search
- `readonly_fields` — fields that can't be edited
- `status_badge()` — custom method that returns colored HTML

**Access:** Go to `/admin/` and log in with a superuser account.

---

## Step 10: REST API

**Files:** `api/serializers.py`, `api/views.py`, `api/urls.py`

### Serializers
- Convert Django model instances to JSON and back
- `WebsiteSerializer` includes nested `recent_checks`
- `read_only_fields` prevents API users from changing status fields

### ViewSets
- `WebsiteViewSet` — full CRUD (Create, Read, Update, Delete)
- Custom actions: `check` (POST) and `history` (GET)
- `ModelViewSet` gives you list/create/retrieve/update/destroy for free

### Router
- `DefaultRouter` auto-generates URL patterns:
  - `GET /api/v1/websites/` — list all
  - `POST /api/v1/websites/` — create new
  - `GET /api/v1/websites/1/` — get one
  - `POST /api/v1/websites/1/check/` — trigger check

---

## Step 11: Celery Background Tasks

**Files:** `multi_web_monitor/celery.py`, `monitors/tasks.py`

### Celery Setup (celery.py)
- Creates a Celery application
- Configures it from Django settings
- `autodiscover_tasks()` — finds all `tasks.py` files in apps

### Tasks (tasks.py)
- `check_website_task(website_id)` — checks one site (with retries)
- `check_all_websites()` — runs every 60s via Celery Beat
- `cleanup_old_checks()` — deletes records older than 30 days (runs at 2 AM)

### __init__.py
- Imports the Celery app so it loads when Django starts

**Note:** Celery requires Redis to be running. Without it, tasks won't run in the background, but the app still works for manual checks.

---

## Step 12: Running the Project

```bash
# 1. Install dependencies
pip install django djangorestframework django-crispy-forms crispy-bootstrap4 httpx celery redis

# 2. Run migrations
python3 manage.py makemigrations monitors
python3 manage.py migrate

# 3. Create admin superuser
python3 manage.py createsuperuser

# 4. Start the development server
python3 manage.py runserver

# 5. (Optional) Start Celery for background checks
celery -A multi_web_monitor worker -l info
celery -A multi_web_monitor beat -l info
```

Visit: http://127.0.0.1:8000/

---

## 🎯 Learning Order Summary

| Step | Topic | File(s) |
|------|-------|---------|
| 1 | Project config | `settings.py` |
| 2 | Database models | `monitors/models.py` |
| 3 | Business logic | `monitors/checker.py` |
| 4 | Forms | `monitors/forms.py` |
| 5 | Views (controllers) | `monitors/views.py` |
| 6 | URL routing | `urls.py` files |
| 7 | Templates (HTML) | `templates/monitors/*.html` |
| 8 | Static files (CSS/JS) | `static/css/`, `static/js/` |
| 9 | Admin panel | `monitors/admin.py` |
| 10 | REST API | `api/` folder |
| 11 | Background tasks | `celery.py`, `tasks.py` |
| 12 | Running it all | Terminal commands |

---

## 💡 Tips

1. **Start simple:** First understand models and views before diving into Celery
2. **Use the admin panel:** It's great for seeing your data without writing views
3. **Read errors carefully:** Django error pages tell you exactly what's wrong
4. **Use `print()` debugging:** Add `print(variable)` in views to see values in terminal
5. **Experiment:** Change things, break things, fix things — that's how you learn!
