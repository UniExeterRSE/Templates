
# Example multipage dash plotly app with authentication

This web application provides an end-to-end workflow for uploading images and reviewing images. It is modular, testable, and organized by domain for clarity and maintainability. This example dash app provides a template for dash apps requiring user authentication and multipage dash. It is based of a bacteria segmentation app, so the bacteria segmentation functionality is stripped out, with upload and review image pages simplified as code might be useful to someone! There is a high level layout in which page content is switched in and out, with the navigation bar menu updated depending on if the user is logged in or not.

## Quickstart

**Install dependencies:**
```bash
uv sync
```

**Run the app:**
```bash
uv run dash-app
```


## Architecture Overview

### Source Code Organization
- **auth/**: Authentication logic, user management, and proxies
- **file_io/**: File and folder utilities, proxy logic for file operations
- **callbacks/**: All Dash callback modules (auto-discovered; place any file with `callbacks` in the name here or in subfolders)
- **pages/**: UI components for each feature, auto-discovered by Dash (place page files here or in subfolders)
- **config.py, app.env**: App configuration and environment variables
- **tests/**: Mirrors the `src/` structure for easy navigation and coverage

### Auto-Discovery System
- **Callbacks**: Place any Python file whose name contains `callbacks` in `src/callbacks/` or any subdirectory (e.g. `src/callbacks/auth/login_callbacks.py`).
  - The app will automatically and recursively import all such files at startup using `register_all_callbacks()` in `dash_app.py`.
  - You do **not** need to manually import or register these files—just follow the naming convention and folder structure.
- **Pages**: Place page files in `src/pages/` or any subdirectory. Pages are auto-registered by Dash if they call `register_page()`.
- **No manual config**: Just follow the folder structure and naming conventions; the app finds everything automatically.

### Adding a New Feature
1. If your feature has interactive logic, add callback files with `callbacks` in the filename to `src/callbacks/` or any subdirectory (e.g. `src/callbacks/myfeature_callbacks.py` or `src/callbacks/app/upload_images_callbacks.py`).
   - You can organize callbacks by subfeature or page as needed, but a feature directory is not required.
2. Add your UI/page files to `src/pages/` or any subdirectory (each should call `register_page()`).
3. Add tests for your feature in `tests/` and/or `tests/callbacks/` to mirror your source structure.
4. No manual imports or config updates are needed—just follow the naming and folder conventions!

## Project Structure
```
pyproject.toml                  # Project metadata and dependencies
README.md                       # Project documentation
uv.lock                         # Lockfile for uv dependencies

src/
├── __init__.py
├── app.env                # Environment variables
├── config.py                   # App configuration
├── dash_app.py                 # Dash app setup, callback/page auto-discovery
├── main.py                     # Application entry point
├── auth/                       # Authentication logic and infrastructure
│   ├── __init__.py
│   ├── authentication.py       # User management, login logic
│   ├── authentication_proxy.py # Proxy for authentication logic
│   └── infrastructure.py       # DB models, Flask app, login manager
├── file_io/                    # File input/output utilities
│   ├── __init__.py
│   ├── file_utilities.py
│   └── file_utilities_proxy.py
├── pages/                      # All Dash pages (auto-discovered, by feature)
│   ├── __init__.py
│   ├── auth/
│   │   ├── login.py
│   │   └── registration.py
│   └── app/
│       ├── select_images.py
│       └── review_images.py
├── callbacks/                  # All Dash callbacks (auto-discovered, by feature)
│   ├── __init__.py
│   ├── layout_callbacks.py
│   ├── auth/
│   │   ├── login_callbacks.py
│   │   └── registration_callbacks.py
│   └── app/
│       ├── select_images_callbacks.p
│       └── review_images_callbacks.py
└── __pycache__/                # Python bytecode cache

data/
├── users.db                    # User database (SQLite)
└── flask_session/              # Flask session files
└── users/                      # User-specific data folders

tests/                          # Test suite mirrors the src/ structure for easy navigation
```
### Pages & Routing
- All user-facing pages are in `src/pages/`, organized by feature
- Pages are auto-registered; just add a file with `register_page()`
- Page-specific callbacks (e.g. for updating layout components) may be defined in the page file for separation of concerns


### Callbacks (Interactive Logic)
- Callbacks handle user interactions and update the UI reactively
- To be auto-discovered, callback files **must** have `callbacks` in their filename (e.g. `login_callbacks.py`, `select_images_callbacks.py`).
- Place these files in `src/callbacks/` or any subdirectory (e.g. `src/callbacks/auth/`, `src/callbacks/app/`).
- Page-specific callbacks can be defined in the page file if they only update that page's layout
- Callbacks handle their own redirects for streamlined user flows (e.g. login, registration, completion)

### Layout System

The layout system manages global navigation and authentication flow across all pages:

- **Authentication-based redirects:** Automatically routes users to the correct page based on authentication (e.g. redirects unauthenticated users to login, and logged-in users away from login/registration).
- **Dynamic navigation/menu:** Updates menu items and visibility based on user status.
- **Centralized logic:** All global layout logic lives in `src/callbacks/layout_callbacks.py` (or similar) and is auto-discovered—no manual imports needed.

This keeps the app secure, user-friendly, and easy to extend.

### Authentication System
The authentication system is fully modular and lives in the `src/auth/` domain for security, maintainability, and testability. It consists of:


- **Infrastructure:** `infrastructure.py` sets up the database models, Flask app, and login manager. This provides the foundation for user storage and session management.
- **Authentication logic:** `authentication.py` implements all user management, login, and registration logic with a clean API. This is the main entry point for authentication operations.
- **Authentication proxy:** `authentication_proxy.py` exposes a testable interface for authentication logic, making it easy to mock or swap out authentication in tests without touching production code.

**Infrastructure Technical Implementation:**
- **Flask-Login Integration**: Uses Flask-Login's `UserMixin`, `login_user()`, `logout_user()`, and `current_user` for session management
- **Database**: SQLite database with SQLAlchemy ORM for user storage
- **User Model**: Simple `User` class with `id`, `username`, and `hashed_password` fields
- **Password Security**: Werkzeug's `generate_password_hash()` and `check_password_hash()` for secure password handling
- **Session Storage**: Flask sessions store user authentication state across requests
- **Database Location**: User database stored in `data/users.db` for persistence

**Testing tip:** For ease of testing, always import the authentication proxy in your code. This allows you to use the authentication mock helper in tests by patching the proxy, without changing production logic.

This structure makes authentication robust, secure, and easy to test. All authentication callbacks are in `src/callbacks/auth/` and all UI is in `src/pages/auth/`.

## Testing

### Running Tests
```bash
uv run pytest
# Or test a specific domain:
uv run pytest tests/auth/
uv run pytest tests/core/
uv run pytest --cov=src
```

### Testing Infrastructure

**Testing & Callback Best Practices:**

- Mirror your test suite structure to `src/` for easy navigation.
- Use centralized fixtures in `conftest.py` to mock authentication, file I/O, and more—focus on business logic, not setup.
- Always import proxies (like `authentication_proxy`, `file_utilities_proxy`) in your code. In tests, patch these proxies to use the mock helpers—this keeps production code clean and makes swapping real/mocks seamless.
- When testing callbacks, always mock only at system boundaries (authentication, file utilities) via proxies—never mock internal business logic. This keeps tests realistic, fast, isolated, and easy to maintain as your app grows.
- Use parameterized tests and shared fixtures to reduce duplication and improve coverage.

---
This approach enables efficient, maintainable, and deterministic testing and development across all domains.

## Getting Started & Development

### 🧪 Running Tests
```bash
# Test everything
uv run pytest

# Test just one part (faster for development)
uv run pytest tests/auth/
uv run pytest tests/core/

# See what's covered by tests
uv run pytest --cov=src
```





