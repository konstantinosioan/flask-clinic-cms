-- Placeholder-only seed data for local development. No real clinic data.

INSERT INTO doctors (name, role, bio, email, phone, photo_filename) VALUES
    ('[Doctor Name]', 'Role', 'placeholder', 'doctor1@gmail.com', '00000000', NULL),
    ('[Doctor Name]', 'Role', 'placeholder', 'doctor2@gmail.com', '00000001', NULL),
    ('[Doctor Name]', 'Role', 'placeholder', 'doctor3@gmail.com', '00000002', NULL);

INSERT INTO clinic_info (phone, email, logo_filename) VALUES
    ('00000000', 'clinic@gmail.com', NULL);

INSERT INTO admins (username, pass_hash) VALUES
    ('admin', 'placeholder');

INSERT INTO announcements (title, body) VALUES
    ('[Announcement Title]', 'placeholder');

INSERT INTO services (name, details) VALUES
    ('[Service Name]', 'placeholder');
