# Flask Clinic CMS

This is a content-management website made for a small medical clinic, built with Python's Flask framework.
It includes a public page and an admin dashboard for managing the doctors, services, gallery photos and announcements.

## Features

- **Public page**: doctors with their details, other services offered by the clinic, a gallery of clinic photos, the clinic's contact details and location map, and an announcements section.
- **Admin dashboard**: add/edit/delete doctors, gallery photos, and announcements; add/delete services; update the clinic's contact info and logo; change the admin password.
- **Image uploads** (doctor photos, gallery photos, and the clinic logo) are validated with Pillow: the file must be a real, decodable image in an allowed format (JPEG, PNG, WEBP, HEIC, or MPO for iPhone support), under 16MB, and under 50 million pixels.
- When a doctor or gallery item is deleted, or its photo is replaced during an edit, the old image file is automatically removed from disk.

## Tech Stack

- **Backend**: Python's Flask (with Jinja2), plain sqlite3
- **Frontend**: Bootstrap (with some CSS), vanilla JavaScript
- **Image processing**: Pillow, pillow-heif (for iPhone support)
- **Config**: python-dotenv
- **Testing**: pytest
- **Dev tools**: pylint, black

## Setup/local run instructions

1. Clone the repo:
   ```
   git clone <repository-url>
   cd flask-clinic-cms
   ```
2. Create and activate a virtual environment (Python 3.x, developed with 3.14):
   ```
   python3 -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up an `.env` file in the project root:
   ```
   SECRET_KEY=your-random-secret-key-here
   ```
5. Build the database:
   ```
   sqlite3 clinic.db < schema.sql
   sqlite3 clinic.db < data.sql
   ```
6. Create the real admin account. `data.sql` seeds an admin row with `'placeholder'` instead of an actual password hash, since there's no signup page by design:
   ```
   python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('YourRealPassword123!'))"
   ```
   Copy the printed hash, then run:
   ```
   sqlite3 clinic.db "UPDATE admins SET pass_hash = 'PASTE_HASH_HERE' WHERE username = 'admin';"
   ```
   - You can set a different username than `admin` at this step too, by also including `username = 'yourname'` in the same `UPDATE` statement — the app has no in-app way to change it afterward, so this is the only point where it's easy to customize.
   - Use a password with at least 8 characters and at least one digit, uppercase letter, and special character — the database itself won't enforce this during setup, but the app's own password rules will require it for any future changes anyway.
7. Run the development server:
   ```
   flask run
   ```
8. Visit `http://127.0.0.1:5000` in your browser (Flask's default) to confirm it works. If that port is already in use, run `flask run --port=5001` instead and visit that port.

The seeded data is placeholder-only (`[Doctor Name]`, `[Clinic Name]`, etc.) — that's expected for local development, not something to fix. See [Placeholder Content](#placeholder-content) below for why.

## Password Recovery

- **No forgot password flow**: There is no forgot password link or any email-based password reset by design
- **Why**: This is a single-admin app with no email infrastructure and limited risk, so building a reset password flow adds unnecessary complexity
- **Recovery path if forgotten**: see [step 6](#setuplocal-run-instructions) above, which involves generating a new hash and updating the admin entry. This requires direct access to the database — not something the admin can do themselves through the app.

## Testing

- **Install dev dependencies**: `pip install -r requirements-dev.txt`
- **Run the tests**: `pytest` (from the project root)
- **Covered**: the `valid_password` function, which enforces the password strength requirements, and the image validation logic (`valid_image`/`save_image`). The scope of the testing is deliberately narrow because this is a small, low-traffic, single-admin app, so a full test suite isn't really worth the effort. Manual testing was done for the rest during development instead.

## Placeholder Content

- **All doctor and clinic data in this repo is fake.** Names like `[Doctor Name]` and `[Clinic Name]`, along with every seeded email, phone number, and bio in `data.sql`, are placeholders — none of it is the real practice's information.
- **This is deliberate, not unfinished work.** The live, deployed site looks completely different because real content is entered by the admin through the actual admin panel after deployment — it's never committed to this repo or seeded directly into the database, even by the developer. That keeps every photo upload passing through the same validated pipeline (Pillow checks, EXIF stripping, etc.) as any other admin-entered content, real or not.
- **Why keep it out of the repo at all**, given the doctor info is meant to be public on the live site anyway: this repo is a public portfolio piece, and permanently tying a real medical practice's identity to a personal GitHub repo is a separate decision from "is this info OK to be public" — so it's kept out on principle, and because git history is permanent.

## Project Structure

```
flask-clinic-cms/
├── app.py                  # Flask routes
├── helpers.py               # Shared helper functions (auth, image validation, etc.)
├── schema.sql                # Database table definitions
├── data.sql                  # Placeholder-only seed data
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt        # Dev dependencies (pytest, pylint, black)
├── .env                     # SECRET_KEY, etc. -- create locally, git-ignored
├── templates/                # Jinja templates
├── static/
│   ├── css/                  # Custom styles
│   ├── js/                   # Vanilla JS enhancements
│   └── uploads/               # Uploaded photos (git-ignored)
└── test/                    # pytest test suite
```