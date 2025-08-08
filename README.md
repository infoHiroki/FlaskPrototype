# Weekly Seminar Video Service

This project is a fully functional web application for a weekly seminar video subscription service, built with Flask. It allows users to register, subscribe via Stripe, and access exclusive video content. Administrators can manage the video library through a dedicated admin panel.

## 📋 Features

- **User Authentication:** Secure user registration, login, and logout.
- **Subscription Management:** Monthly subscription handling via Stripe Checkout.
- **Stripe Integration:**
    - Secure payment processing.
    - Webhook handling for real-time subscription status updates.
    - Customer Portal for users to manage their subscriptions.
- **Protected Content:** Video content is exclusively available to users with an active subscription.
- **Admin Panel:** A protected dashboard for administrators to add and edit video content.
- **Modular Architecture:** The application is built using Flask Blueprints for better organization.

## 🛠️ Tech Stack

- **Backend:** Flask, Python 3.11+
- **Database:** SQLAlchemy, Flask-Migrate (designed for PostgreSQL, uses SQLite for local dev)
- **Authentication:** Flask-Login
- **Payments:** Stripe API
- **Video Hosting:** Vimeo (embedded player)
- **WSGI Server:** Gunicorn

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.11 or higher
- `pip` for package management

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a file named `.env` in the root of the project directory and add the following variables.

    ```dotenv
    # Flask
    SECRET_KEY='a_very_secret_key_that_should_be_changed'
    FLASK_APP=run.py
    FLASK_ENV=development

    # Database (Use your PostgreSQL URL or keep SQLite for testing)
    DATABASE_URL='sqlite:///app.db'
    # Example for PostgreSQL: DATABASE_URL='postgresql://user:password@host:port/dbname'

    # Stripe
    STRIPE_PUBLISHABLE_KEY='pk_test_...' # Your Stripe publishable key
    STRIPE_SECRET_KEY='sk_test_...'     # Your Stripe secret key
    STRIPE_PRICE_ID='price_...'         # The ID of your Stripe subscription price
    STRIPE_WEBHOOK_SECRET='whsec_...'   # Your Stripe webhook signing secret
    ```

5.  **Initialize the database:**
    Run the following commands to create the database schema.
    ```bash
    flask db upgrade
    ```
    *(Note: If you are starting from scratch without a `migrations` folder, run `flask db init` first, then `flask db migrate -m "Initial migration"`, then `flask db upgrade`)*

### Running the Application

To start the development server, run:
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000`.

### Creating an Admin User

To access the admin panel, you need to manually set a user's `is_admin` flag to `True` in the database.

1.  Register a new user through the web interface.
2.  Open a `flask shell`:
    ```bash
    flask shell
    ```
3.  In the shell, run the following commands, replacing `'admin@example.com'` with the email of the user you want to make an admin:
    ```python
    from app.models import User
    from app import db
    u = User.query.filter_by(email='admin@example.com').first()
    if u:
        u.is_admin = True
        db.session.commit()
        print(f"User {u.email} is now an admin.")
    else:
        print("User not found.")
    ```
