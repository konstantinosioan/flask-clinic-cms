CREATE TABLE doctors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    bio TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    photo_filename TEXT
);

CREATE TABLE gallery (
    id INTEGER PRIMARY KEY,
    image_filename TEXT NOT NULL,
    caption TEXT
);

CREATE TABLE clinic_info (
    id INTEGER PRIMARY KEY,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    instagram_url TEXT,
    facebook_url TEXT,
    hours TEXT,
    logo_filename TEXT NOT NULL
);

CREATE TABLE admins (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    pass_hash TEXT NOT NULL
);

CREATE TABLE announcements (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    details TEXT NOT NULL
);