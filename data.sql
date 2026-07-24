-- Placeholder-only seed data for local development. No real clinic data.

INSERT INTO doctors (name, role, bio, email, phone, photo_filename) VALUES
    ('[Doctor Name]', 'Role', 'placeholder', 'doctor1@gmail.com', '00000000', NULL),
    ('[Doctor Name]', 'Role', 'placeholder', 'doctor2@gmail.com', '00000001', NULL),
    ('[Doctor Name]', 'Role', 'placeholder', 'doctor3@gmail.com', '00000002', NULL);

INSERT INTO gallery (image_filename, caption) VALUES
    (NULL, 'Placeholder'),
    (NULL, 'Placeholder');

INSERT INTO clinic_info (phone, email) VALUES
    ('00000000', 'clinic@gmail.com');

INSERT INTO admins (username, pass_hash) VALUES
    ('admin', 'placeholder');
