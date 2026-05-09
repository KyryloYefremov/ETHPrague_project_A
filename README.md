# ETHPrague Project A

`ETHPrague_project_A` is a Flask-based blog application with user authentication, rich-text post publishing, and a comment system. The UI is currently branded in templates as `Angela's Blog`, but the codebase is a reusable starter for a small content platform or personal publishing app.

The project uses server-rendered Flask templates, SQLAlchemy models, Flask-Login for session management, and CKEditor for rich-text editing. It supports local development with SQLite out of the box and can be deployed with Gunicorn using a production database URL from the environment.

## Features

- User registration and login with hashed passwords
- Session-based authentication via `Flask-Login`
- Admin-only post creation, editing, and deletion
- Rich-text blog posts using `Flask-CKEditor`
- Authenticated comments on individual posts
- Gravatar-based avatars for comment authors
- Bootstrap-based responsive UI with Jinja templates
- Automatic database table creation on startup
- SQLite by default, with support for a remote database through `DB_URI`
- Production-ready Gunicorn entrypoint via `Procfile.`

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-Login
- Flask-WTF / WTForms
- Flask-CKEditor
- Bootstrap-Flask
- Gunicorn
- `psycopg2-binary` for PostgreSQL-compatible deployments

## Project Structure

```text
ETHPrague_project_A/
├── forms.py                 # WTForms for posts, auth, and comments
├── main.py                  # Flask app, models, routes, and DB setup
├── requirements.txt         # Python dependencies
├── Procfile.                # Gunicorn process definition
├── static/
│   ├── assets/              # Images, favicon, theme assets
│   ├── css/styles.css       # Main stylesheet
│   └── js/scripts.js        # Frontend theme scripts
└── templates/
    ├── header.html
    ├── footer.html
    ├── index.html
    ├── post.html
    ├── make-post.html
    ├── login.html
    ├── register.html
    ├── about.html
    └── contact.html
```

## How It Works

### Authentication

- Users can register with a name, email, and password.
- Passwords are stored as hashes using Werkzeug's `generate_password_hash`.
- Users log in through `Flask-Login`, which manages the session.
- Logged-in users can leave comments on posts.

### Authorization

- Post management is protected by the `admin_only` decorator.
- The current admin rule is simple: only the user with `id == 1` can create, edit, or delete posts.
- Unauthenticated users or non-admin users receive `403 Forbidden` for admin routes.

### Content Management

- Posts include a title, subtitle, hero image URL, publication date, and rich-text body.
- The post editor uses CKEditor for formatted content.
- The homepage lists all posts.
- Individual post pages display the full article and all comments.

### Database

The application defines three SQLAlchemy models:

- `User`
  - `id`
  - `name`
  - `email`
  - `password`
- `BlogPost`
  - `id`
  - `author_id`
  - `title`
  - `subtitle`
  - `date`
  - `body`
  - `img_url`
- `Comment`
  - `id`
  - `author_id`
  - `post_id`
  - `text`

Relationships:

- One `User` can author many `BlogPost` records.
- One `User` can author many `Comment` records.
- One `BlogPost` can have many `Comment` records.

Tables are created automatically when the app starts:

```python
with app.app_context():
    db.create_all()
```

## Routes

| Route | Methods | Purpose |
|---|---|---|
| `/` | `GET` | Show all blog posts |
| `/register` | `GET`, `POST` | Register a new user |
| `/login` | `GET`, `POST` | Log in an existing user |
| `/logout` | `GET` | Log out the current user |
| `/post/<post_id>` | `GET`, `POST` | View a post and submit comments |
| `/new-post` | `GET`, `POST` | Create a new post, admin only |
| `/edit-post/<post_id>` | `GET`, `POST` | Edit a post, admin only |
| `/delete/<post_id>` | `GET` | Delete a post, admin only |
| `/about` | `GET` | About page |
| `/contact` | `GET` | Contact page |

## Local Development Setup

### 1. Create and activate a virtual environment

```bash
cd ETHPrague_project_A
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Export environment variables

`FLASK_KEY` is required for secure sessions and WTForms CSRF protection. `DB_URI` is optional.

```bash
export FLASK_KEY="replace-this-with-a-secret-value"
export DB_URI="sqlite:///posts.db"
```

If `DB_URI` is not set, the app falls back to:

```text
sqlite:///posts.db
```

### 4. Run the app

```bash
python main.py
```

The application starts on:

```text
http://127.0.0.1:5002
```

## Production Run

The repository includes a Gunicorn process definition:

```text
web: gunicorn main:app
```

Example:

```bash
gunicorn main:app
```

For production, provide:

- `FLASK_KEY`
- `DB_URI`

A PostgreSQL connection string is a typical fit here, which is why `psycopg2-binary` is included in `requirements.txt`.

## First Admin User

This app does not currently have a role system. The first registered user becomes the effective admin because admin access is hardcoded to `current_user.id == 1`.

Practical implication:

- Register the first account carefully in a fresh database.
- If you reset the database, the first created user will again be the admin.

## Forms

Defined in `forms.py`:

- `CreatePostForm`
  - Title
  - Subtitle
  - Image URL
  - Rich-text body
- `RegisterForm`
  - Name
  - Email
  - Password
- `LoginForm`
  - Email
  - Password
- `CommentForm`
  - Rich-text comment

## Notes and Limitations

- There is no explicit role model beyond the `id == 1` admin check.
- Database migrations are not set up; schema is created directly with `db.create_all()`.
- The app uses server-rendered templates rather than a separate frontend client.
- Comments require authentication, but reading posts does not.
- Some branding in the templates still refers to `Angela's Blog` and `Start Bootstrap`.

## Suggested Improvements

- Add a proper `is_admin` or role-based authorization model
- Introduce database migrations with Flask-Migrate or Alembic
- Add `.env` loading with `python-dotenv`
- Add automated tests for auth, post CRUD, and comments
- Add pagination for the homepage post list
- Add profile pages and post ownership rules
- Add validation or upload support for post cover images

## Dependencies

Current dependencies from `requirements.txt`:

- `Bootstrap_Flask==2.2.0`
- `Flask==2.2.5`
- `Flask_CKEditor==0.4.6`
- `Flask_Login==0.6.2`
- `Flask-Gravatar==0.5.0`
- `flask_sqlalchemy==3.0.5`
- `Flask_WTF==1.1.1`
- `Werkzeug==2.2.3`
- `WTForms==3.0.1`
- `SQLAlchemy==2.0.19`
- `gunicorn==21.2.0`
- `psycopg2-binary==2.9.6`

## Summary

This project is a compact full-stack Flask blogging platform with authentication, admin-managed publishing, and user comments. It is suitable as a learning project, a starter codebase for a small CMS-style app, or a base for extending into a more complete publishing platform.
