
# SalonSaaS

**A Multi-Business Salon and Barbershop Management Platform**

SalonSaaS is a Django-powered web application designed to help salon and barbershop businesses manage their daily operations through a centralised platform.

The system is being developed to support multiple businesses, customer interactions, appointment management, employee administration and business operations.

## Project Objectives

The goal of SalonSaaS is to simplify salon management by bringing important business activities together in one application.

The project demonstrates practical software development skills, including backend development, database management, authentication, role-based access control and full-stack web development.

## Core Features

- **Customer Management:** Customer registration, authentication and profile management.
- **Business Management:** Support for multiple salons and barbershops.
- **Appointment Management:** Appointment booking, viewing and cancellation workflows.
- **Scheduling:** Business availability and appointment scheduling.
- **Service Management:** Management of salon and barbershop services.
- **Employee Management:** Business staff administration.
- **Notifications:** Customer and business notification management.
- **Role-Based Access:** Different permissions for platform administrators, business owners and staff.

## Additional Business Modules

The project structure also includes modules for:

- Sales management
- Expense management
- Inventory management
- Business reporting
- Subscription management

These modules are part of the broader development scope, with implementation and integration progressing over time.

## Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Django |
| Frontend | HTML, CSS, JavaScript |
| Database | SQLite (Development) |
| Image Processing | Pillow |
| Version Control | Git and GitHub |

## Project Structure

```text
SalonSaaS/
│
├── accounts/
├── appointments/
├── businesses/
├── customers/
├── employees/
├── expenses/
├── inventory/
├── notifications/
├── reports/
├── sales/
├── scheduling/
├── services/
├── subscriptions/
│
├── config/
├── templates/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13
- Git
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Lisakhanya5962/SalonSaaS.git
cd SalonSaaS
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```cmd
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

On Windows Command Prompt:

```cmd
set DJANGO_SECRET_KEY=your-new-secret-key
set DJANGO_DEBUG=True
set DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Generate a new secret key for your own environment. Never publish real credentials.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an administrator account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Visit:

http://127.0.0.1:8000/

## Screenshots

Application screenshots and demonstrations will be added here as development progresses.

## Development Status

SalonSaaS is an ongoing development project.

The application is being developed with a focus on maintainability, modular architecture, secure authentication and practical business workflows.

The repository showcases the source code and development process. It is not currently presented as a production-ready deployment.

## Developer

**Lisakhanya Mbusi**

Diploma in Information Technology (Software Development)
Nelson Mandela University

**Technical Interests**

- Python and Django Development
- Full-Stack Web Development
- Database Design and Management
- Backend Application Development
- Software Engineering

## License

This project is shared for portfolio and demonstration purposes. All rights reserved.

(salon_saas) C:\Users\User\Documents\LISA\LISA\SalonSaaS>for /d /r %d in (migrations) do @if exist "%d\__init__.py" dir /b "%d\*.py"
0001_initial.py
0002_alter_user_role.py
__init__.py
0001_initial.py
__init__.py
0001_initial.py
0002_businessmembership.py
__init__.py
0001_initial.py
0002_customer_user.py
__init__.py
0001_initial.py
__init__.py
__init__.py
__init__.py
0001_initial.py
__init__.py
__init__.py
__init__.py
0001_initial.py
__init__.py
0001_initial.py
__init__.py
__init__.py

(salon_saas) C:\Users\User\Documents\LISA\LISA\SalonSaaS>python manage.py showmigrations
accounts
 [X] 0001_initial
 [X] 0002_alter_user_role
admin
 [X] 0001_initial
 [X] 0002_logentry_remove_auto_add
 [X] 0003_logentry_add_action_flag_choices
appointments
 [X] 0001_initial
auth
 [X] 0001_initial
 [X] 0002_alter_permission_name_max_length
 [X] 0003_alter_user_email_max_length
 [X] 0004_alter_user_username_opts
 [X] 0005_alter_user_last_login_null
 [X] 0006_require_contenttypes_0002
 [X] 0007_alter_validators_add_error_messages
 [X] 0008_alter_user_username_max_length
 [X] 0009_alter_user_last_name_max_length
 [X] 0010_alter_group_name_max_length
 [X] 0011_update_proxy_permissions
 [X] 0012_alter_user_first_name_max_length
businesses
 [X] 0001_initial
 [X] 0002_businessmembership
contenttypes
 [X] 0001_initial
 [X] 0002_remove_content_type_name
customers
 [X] 0001_initial
 [X] 0002_customer_user
employees
 [X] 0001_initial
notifications
 [X] 0001_initial
scheduling
 [X] 0001_initial
services
 [X] 0001_initial
sessions
 [X] 0001_initial

(salon_saas) C:\Users\User\Documents\LISA\LISA\SalonSaaS>git ls-files --others --exclude-standard
.gitignore
README.md
accounts/__init__.py
accounts/admin.py
accounts/apps.py
accounts/forms.py
accounts/migrations/0001_initial.py
accounts/migrations/0002_alter_user_role.py
accounts/migrations/__init__.py
accounts/models.py
accounts/templates/accounts/add_staff.html
accounts/templates/accounts/customer_businesses.html
accounts/templates/accounts/customer_register.html
accounts/templates/accounts/edit_staff.html
accounts/templates/accounts/login.html
accounts/templates/accounts/register.html
accounts/templates/accounts/staff_list.html
accounts/tests.py
accounts/urls.py
accounts/views.py
appointments/__init__.py
appointments/admin.py
appointments/apps.py
appointments/forms.py
appointments/migrations/0001_initial.py
appointments/migrations/__init__.py
appointments/models.py
appointments/templates/appointments/appointment_detail.html
appointments/templates/appointments/appointment_form.html
appointments/templates/appointments/appointment_list.html
appointments/templates/appointments/calendar.html
appointments/templatetags/__init__.py
appointments/templatetags/appointment_extras.py
appointments/templatetags/calendar_filters.py
appointments/templatetags/calendar_tags.py
appointments/tests.py
appointments/urls.py
appointments/views.py
businesses/__init__.py
businesses/admin.py
businesses/apps.py
businesses/migrations/0001_initial.py
businesses/migrations/0002_businessmembership.py
businesses/migrations/__init__.py
businesses/models.py
businesses/tests.py
businesses/views.py
config/__init__.py
config/asgi.py
config/context_processors/__init__.py
config/context_processors/business.py
config/context_processors/notifications.py
config/settings.py
config/urls.py
config/views.py
config/wsgi.py
customers/__init__.py
customers/admin.py
customers/apps.py
customers/forms.py
customers/migrations/0001_initial.py
customers/migrations/0002_customer_user.py
customers/migrations/__init__.py
customers/models.py
customers/templates/customers/customer_detail.html
customers/templates/customers/customer_form.html
customers/templates/customers/customer_list.html
customers/tests.py
customers/urls.py
customers/views.py
employees/__init__.py
employees/admin.py
employees/apps.py
employees/migrations/0001_initial.py
employees/migrations/__init__.py
employees/models.py
employees/tests.py
employees/views.py
expenses/__init__.py
expenses/admin.py
expenses/apps.py
expenses/migrations/__init__.py
expenses/models.py
expenses/tests.py
expenses/views.py
inventory/__init__.py
inventory/admin.py
inventory/apps.py
inventory/migrations/__init__.py
inventory/models.py
inventory/tests.py
inventory/views.py
manage.py
notifications/__init__.py
notifications/admin.py
notifications/apps.py
notifications/migrations/0001_initial.py
notifications/migrations/__init__.py
notifications/models.py
notifications/tests.py
notifications/urls.py
notifications/utils.py
notifications/views.py
reports/__init__.py
reports/admin.py
reports/apps.py
reports/migrations/__init__.py
reports/models.py
reports/tests.py
reports/views.py
requirements.txt
sales/__init__.py
sales/admin.py
sales/apps.py
sales/migrations/__init__.py
sales/models.py
sales/tests.py
sales/views.py
scheduling/__init__.py
scheduling/admin.py
scheduling/apps.py
scheduling/forms.py
scheduling/migrations/0001_initial.py
scheduling/migrations/__init__.py
scheduling/models.py
scheduling/templates/scheduling/availability_confirm_delete.html
scheduling/templates/scheduling/availability_form.html
scheduling/templates/scheduling/availability_list.html
scheduling/tests.py
scheduling/urls.py
scheduling/views.py
services/__init__.py
services/admin.py
services/apps.py
services/forms.py
services/migrations/0001_initial.py
services/migrations/__init__.py
services/models.py
services/templates/services/service_form.html
services/templates/services/service_list.html
services/tests.py
services/urls.py
services/views.py
subscriptions/__init__.py
subscriptions/admin.py
subscriptions/apps.py
subscriptions/migrations/__init__.py
subscriptions/models.py
subscriptions/tests.py
subscriptions/views.py
templates/accounts/customer_dashboard.html
templates/accounts/customer_login.html
templates/accounts/customer_profile.before_cleanup.html
templates/accounts/customer_profile.html
templates/appointments/calendar.html
templates/appointments/customer_appointment_detail.html
templates/appointments/customer_booking.html
templates/appointments/customer_calendar.html
templates/base.html
templates/dashboard.before_cleanup.html
templates/dashboard.html
templates/landing.html
templates/notifications/notification_list.html
