-- ===================================================================
-- DATABASE SCHEMA UNTUK ENHANCED UNIVERSITY SCHEDULING SYSTEM
-- ===================================================================
-- Sistem Penjadwalan Kuliah dengan fitur Reserved Slots dan Enhanced Preferences
-- Kompatibel dengan MySQL, PostgreSQL, dan SQLite

-- ===================================================================
-- 1. TABEL MASTER DATA
-- ===================================================================

-- Tabel untuk data mata kuliah
CREATE TABLE kuliah_teknik (
    id INT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    dosen VARCHAR(50) NOT NULL,
    sks INT NOT NULL CHECK (sks >= 1 AND sks <= 6),
    semester INT DEFAULT 1,
    kode_mk VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk optimasi query
CREATE INDEX idx_kuliah_dosen ON kuliah_teknik(dosen);
CREATE INDEX idx_kuliah_semester ON kuliah_teknik(semester);

-- Tabel untuk slot waktu yang tersedia
CREATE TABLE waktu2 (
    id INT PRIMARY KEY,
    hari VARCHAR(20) NOT NULL,
    jam_mulai TIME NOT NULL,
    jam_selesai TIME,
    session_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk optimasi query waktu
CREATE INDEX idx_waktu_hari ON waktu2(hari);
CREATE INDEX idx_waktu_jam ON waktu2(jam_mulai);

-- Tabel untuk data ruangan
CREATE TABLE ruangan (
    id INT PRIMARY KEY,
    nama VARCHAR(50) NOT NULL,
    kapasitas INT NOT NULL CHECK (kapasitas > 0),
    tipe_ruang VARCHAR(30) DEFAULT 'Kelas',
    fasilitas TEXT,
    lokasi VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk optimasi query ruangan
CREATE INDEX idx_ruangan_tipe ON ruangan(tipe_ruang);
CREATE INDEX idx_ruangan_kapasitas ON ruangan(kapasitas);

-- ===================================================================
-- 2. TABEL PREFERENSI DOSEN (BASIC)
-- ===================================================================

-- Tabel preferensi dosen basic (kompatibilitas dengan sistem lama)
CREATE TABLE preferensi_waktu_dosen (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dosen VARCHAR(50) NOT NULL,
    preferensi_waktu TEXT, -- JSON array format: [0,2,4,6]
    tidak_bisa_waktu TEXT, -- JSON array format: [8,1]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Index untuk dosen
CREATE INDEX idx_preferensi_dosen ON preferensi_waktu_dosen(dosen);

-- ===================================================================
-- 3. TABEL ENHANCED PREFERENCES (FITUR BARU)
-- ===================================================================

-- Tabel untuk reserved slots (exclusive time slots)
CREATE TABLE reserved_slots (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dosen VARCHAR(50) NOT NULL,
    waktu_id INT NOT NULL,
    ruang_id INT NULL, -- NULL berarti any room
    priority VARCHAR(20) DEFAULT 'exclusive',
    reason TEXT,
    is_recurring BOOLEAN DEFAULT FALSE,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (waktu_id) REFERENCES waktu2(id),
    FOREIGN KEY (ruang_id) REFERENCES ruangan(id)
);

-- Index untuk reserved slots
CREATE INDEX idx_reserved_dosen ON reserved_slots(dosen);
CREATE INDEX idx_reserved_waktu ON reserved_slots(waktu_id);
CREATE INDEX idx_reserved_ruang ON reserved_slots(ruang_id);

-- Tabel untuk preferred slots
CREATE TABLE preferred_slots (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dosen VARCHAR(50) NOT NULL,
    waktu_id INT NOT NULL,
    priority_level VARCHAR(20) DEFAULT 'medium', -- high, medium, low
    weight_score INT DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (waktu_id) REFERENCES waktu2(id)
);

-- Index untuk preferred slots
CREATE INDEX idx_preferred_dosen ON preferred_slots(dosen);
CREATE INDEX idx_preferred_priority ON preferred_slots(priority_level);

-- Tabel untuk blocked slots
CREATE TABLE blocked_slots (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dosen VARCHAR(50) NOT NULL,
    waktu_id INT NOT NULL,
    reason TEXT,
    is_permanent BOOLEAN DEFAULT TRUE,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (waktu_id) REFERENCES waktu2(id)
);

-- Index untuk blocked slots
CREATE INDEX idx_blocked_dosen ON blocked_slots(dosen);
CREATE INDEX idx_blocked_waktu ON blocked_slots(waktu_id);

-- Tabel untuk flexible slots
CREATE TABLE flexible_slots (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dosen VARCHAR(50) NOT NULL,
    waktu_id INT NOT NULL,
    priority_level VARCHAR(20) DEFAULT 'low', -- high, medium, low
    weight_score INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (waktu_id) REFERENCES waktu2(id)
);

-- Index untuk flexible slots
CREATE INDEX idx_flexible_dosen ON flexible_slots(dosen);

-- ===================================================================
-- 4. TABEL HASIL SCHEDULING
-- ===================================================================

-- Tabel untuk menyimpan hasil scheduling
CREATE TABLE schedule_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_name VARCHAR(100),
    kuliah_id INT NOT NULL,
    waktu_id INT NOT NULL,
    ruang_id INT NOT NULL,
    fitness_score DECIMAL(10,6),
    generation_found INT,
    has_violations BOOLEAN DEFAULT FALSE,
    violation_details TEXT, -- JSON format
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kuliah_id) REFERENCES kuliah_teknik(id),
    FOREIGN KEY (waktu_id) REFERENCES waktu2(id),
    FOREIGN KEY (ruang_id) REFERENCES ruangan(id)
);

-- Index untuk schedule results
CREATE INDEX idx_schedule_session ON schedule_results(session_name);
CREATE INDEX idx_schedule_fitness ON schedule_results(fitness_score);

-- Tabel untuk log scheduling process
CREATE TABLE scheduling_logs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_name VARCHAR(100),
    generation INT,
    best_fitness DECIMAL(10,6),
    total_penalties INT,
    reserved_violations INT,
    preference_violations INT,
    traditional_clashes INT,
    execution_time DECIMAL(10,3),
    ram_usage INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===================================================================
-- 5. SAMPLE DATA
-- ===================================================================

-- Insert sample kuliah data
INSERT INTO kuliah_teknik (id, nama, dosen, sks, semester, kode_mk) VALUES 
(0, 'Algoritma & Pemrograman', 'Dr. Ahmad', 3, 1, 'IF101'),
(1, 'Basis Data', 'Dr. Budi', 3, 3, 'IF201'),
(2, 'Jaringan Komputer', 'Dr. Ahmad', 2, 5, 'IF301'),
(3, 'Sistem Operasi', 'Dr. Citra', 3, 4, 'IF202'),
(4, 'Pemrograman Web', 'Dr. Budi', 2, 3, 'IF203'),
(5, 'Struktur Data', 'Dr. Ahmad', 3, 2, 'IF102'),
(6, 'Kecerdasan Buatan', 'Prof. Dr. Wiranto', 3, 7, 'IF401'),
(7, 'Machine Learning', 'Dr. Lisa Sari', 3, 7, 'IF402'),
(8, 'Cyber Security', 'Dr. Bambang Praktek', 2, 6, 'IF302');

-- Insert sample waktu data
INSERT INTO waktu2 (id, hari, jam_mulai, jam_selesai, session_name) VALUES 
(0, 'Senin', '08:00', '09:40', 'Sesi 1'),
(1, 'Senin', '10:00', '11:40', 'Sesi 2'),
(2, 'Selasa', '08:00', '09:40', 'Sesi 1'),
(3, 'Selasa', '10:00', '11:40', 'Sesi 2'),
(4, 'Rabu', '08:00', '09:40', 'Sesi 1'),
(5, 'Rabu', '10:00', '11:40', 'Sesi 2'),
(6, 'Kamis', '08:00', '09:40', 'Sesi 1'),
(7, 'Kamis', '10:00', '11:40', 'Sesi 2'),
(8, 'Jumat', '08:00', '09:40', 'Sesi 1'),
(9, 'Jumat', '13:00', '14:40', 'Sesi 2'),
(10, 'Sabtu', '08:00', '09:40', 'Sesi Weekend');

-- Insert sample ruangan data
INSERT INTO ruangan (id, nama, kapasitas, tipe_ruang, fasilitas, lokasi) VALUES 
(0, 'Lab Komputer 1', 30, 'Laboratory', 'PC, Projector, AC', 'Lantai 2'),
(1, 'Lab Komputer 2', 25, 'Laboratory', 'PC, Projector, AC', 'Lantai 2'),
(2, 'Ruang Kelas A', 40, 'Classroom', 'Projector, AC, Whiteboard', 'Lantai 1'),
(3, 'Ruang Kelas B', 35, 'Classroom', 'Projector, AC, Whiteboard', 'Lantai 1'),
(4, 'Auditorium', 100, 'Auditorium', 'Sound System, Projector, AC', 'Lantai 3'),
(5, 'Lab Jaringan', 20, 'Laboratory', 'Network Equipment, PC', 'Lantai 3');

-- Insert sample preferensi basic
INSERT INTO preferensi_waktu_dosen (dosen, preferensi_waktu, tidak_bisa_waktu) VALUES 
('Dr. Ahmad', '[0,2,4]', '[8]'),
('Dr. Budi', '[1,3,5]', '[0]'),
('Dr. Citra', '[6,7]', '[1,8]'),
('Prof. Dr. Wiranto', '[1,2,5]', '[8,9]'),
('Dr. Lisa Sari', '[0,2,4,6]', '[8]'),
('Dr. Bambang Praktek', '[0,2]', '[3,4,5,6,7,8]');

-- Insert sample reserved slots (exclusive time slots)
INSERT INTO reserved_slots (dosen, waktu_id, ruang_id, reason, is_recurring) VALUES 
('Prof. Dr. Wiranto', 1, 0, 'Weekly research meeting with PhD students', TRUE),
('Prof. Dr. Wiranto', 5, NULL, 'Senate meeting - any room', TRUE),
('Dr. Bambang Praktek', 1, NULL, 'Clinic practice - exclusive morning slot', TRUE);

-- Insert sample preferred slots
INSERT INTO preferred_slots (dosen, waktu_id, priority_level, weight_score) VALUES 
('Dr. Ahmad', 2, 'high', 50),
('Dr. Ahmad', 4, 'high', 50),
('Dr. Budi', 3, 'high', 50),
('Dr. Budi', 6, 'medium', 30),
('Dr. Citra', 7, 'high', 50),
('Dr. Lisa Sari', 0, 'high', 50),
('Dr. Lisa Sari', 2, 'medium', 30);

-- Insert sample blocked slots
INSERT INTO blocked_slots (dosen, waktu_id, reason, is_permanent) VALUES 
('Prof. Dr. Wiranto', 8, 'Jumatan - Friday prayer', TRUE),
('Prof. Dr. Wiranto', 7, 'Hospital duty', TRUE),
('Dr. Ahmad', 8, 'Jumatan', TRUE),
('Dr. Budi', 8, 'Jumatan', TRUE),
('Dr. Citra', 8, 'Jumatan', TRUE),
('Dr. Lisa Sari', 8, 'Jumatan', TRUE),
('Dr. Bambang Praktek', 3, 'Clinic duty afternoon', TRUE),
('Dr. Bambang Praktek', 4, 'Clinic duty afternoon', TRUE),
('Dr. Bambang Praktek', 5, 'Clinic duty afternoon', TRUE),
('Dr. Bambang Praktek', 6, 'Clinic duty afternoon', TRUE),
('Dr. Bambang Praktek', 7, 'Clinic duty afternoon', TRUE),
('Dr. Bambang Praktek', 8, 'Jumatan', TRUE);

-- Insert sample flexible slots
INSERT INTO flexible_slots (dosen, waktu_id, priority_level, weight_score) VALUES 
('Dr. Ahmad', 0, 'medium', 30),
('Dr. Ahmad', 3, 'low', 10),
('Dr. Budi', 1, 'medium', 30),
('Dr. Budi', 4, 'low', 10),
('Dr. Citra', 0, 'medium', 30),
('Dr. Citra', 2, 'low', 10),
('Dr. Lisa Sari', 1, 'medium', 30),
('Dr. Lisa Sari', 3, 'medium', 30),
('Dr. Lisa Sari', 4, 'low', 10),
('Dr. Lisa Sari', 6, 'low', 10);

-- ===================================================================
-- 6. VIEWS UNTUK KEMUDAHAN QUERY
-- ===================================================================

-- View untuk melihat schedule dengan detail lengkap
CREATE VIEW v_schedule_detail AS
SELECT 
    sr.id,
    sr.session_name,
    k.nama as mata_kuliah,
    k.dosen,
    k.sks,
    w.hari,
    w.jam_mulai,
    w.jam_selesai,
    r.nama as ruangan,
    r.kapasitas,
    sr.fitness_score,
    sr.has_violations,
    sr.created_at
FROM schedule_results sr
JOIN kuliah_teknik k ON sr.kuliah_id = k.id
JOIN waktu2 w ON sr.waktu_id = w.id
JOIN ruangan r ON sr.ruang_id = r.id;

-- View untuk melihat reserved slots dengan detail
CREATE VIEW v_reserved_slots_detail AS
SELECT 
    rs.id,
    rs.dosen,
    w.hari,
    w.jam_mulai,
    w.session_name,
    r.nama as ruangan,
    rs.reason,
    rs.is_recurring,
    rs.created_at
FROM reserved_slots rs
JOIN waktu2 w ON rs.waktu_id = w.id
LEFT JOIN ruangan r ON rs.ruang_id = r.id;

-- View untuk analytics dashboard
CREATE VIEW v_scheduling_analytics AS
SELECT 
    session_name,
    COUNT(*) as total_schedules,
    AVG(fitness_score) as avg_fitness,
    COUNT(CASE WHEN has_violations = TRUE THEN 1 END) as schedules_with_violations,
    MAX(generation_found) as max_generations,
    MAX(created_at) as last_run
FROM schedule_results
GROUP BY session_name;

-- ===================================================================
-- 7. STORED PROCEDURES (MySQL/PostgreSQL)
-- ===================================================================

-- Procedure untuk clear old scheduling data
DELIMITER //
CREATE PROCEDURE ClearOldSchedulingData(IN days_old INT)
BEGIN
    DELETE FROM scheduling_logs WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY);
    DELETE FROM schedule_results WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY);
END //
DELIMITER ;

-- Function untuk get enhanced preferences (returning JSON)
DELIMITER //
CREATE FUNCTION GetEnhancedPreferences(dosen_name VARCHAR(50))
RETURNS JSON
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE result JSON;
    
    SELECT JSON_OBJECT(
        'reserved_slots', (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'waktu', waktu_id,
                    'ruang', ruang_id,
                    'priority', priority,
                    'reason', reason
                )
            )
            FROM reserved_slots WHERE dosen = dosen_name
        ),
        'preferred_slots', (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'waktu', waktu_id,
                    'priority', priority_level
                )
            )
            FROM preferred_slots WHERE dosen = dosen_name
        ),
        'blocked_slots', (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'waktu', waktu_id,
                    'reason', reason
                )
            )
            FROM blocked_slots WHERE dosen = dosen_name
        ),
        'flexible_slots', (
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'waktu', waktu_id,
                    'priority', priority_level
                )
            )
            FROM flexible_slots WHERE dosen = dosen_name
        )
    ) INTO result;
    
    RETURN result;
END //
DELIMITER ;

-- ===================================================================
-- 8. INDEXES UNTUK PERFORMANCE
-- ===================================================================

-- Composite indexes untuk query yang sering digunakan
CREATE INDEX idx_schedule_session_fitness ON schedule_results(session_name, fitness_score);
CREATE INDEX idx_reserved_dosen_waktu ON reserved_slots(dosen, waktu_id);
CREATE INDEX idx_preferred_dosen_priority ON preferred_slots(dosen, priority_level);

-- Full-text search indexes (MySQL)
-- ALTER TABLE kuliah_teknik ADD FULLTEXT(nama);
-- ALTER TABLE reserved_slots ADD FULLTEXT(reason);

-- ===================================================================
-- 9. TRIGGERS UNTUK DATA INTEGRITY
-- ===================================================================

-- Trigger untuk prevent conflicting reserved slots
DELIMITER //
CREATE TRIGGER prevent_reserved_conflict
BEFORE INSERT ON reserved_slots
FOR EACH ROW
BEGIN
    DECLARE conflict_count INT;
    
    -- Check if same time-room combination already reserved
    SELECT COUNT(*) INTO conflict_count
    FROM reserved_slots 
    WHERE waktu_id = NEW.waktu_id 
    AND (ruang_id = NEW.ruang_id OR ruang_id IS NULL OR NEW.ruang_id IS NULL)
    AND dosen != NEW.dosen;
    
    IF conflict_count > 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Reserved slot conflict detected!';
    END IF;
END //
DELIMITER ;

-- Trigger untuk automatic timestamps
DELIMITER //
CREATE TRIGGER update_preferensi_timestamp
BEFORE UPDATE ON preferensi_waktu_dosen
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END //
DELIMITER ;

-- ===================================================================
-- 10. EXAMPLE QUERIES
-- ===================================================================

-- Query untuk mendapatkan enhanced preferences dalam format Python
/*
SELECT 
    dosen,
    CONCAT('{', 
        '"reserved_slots": ', IFNULL(
            (SELECT CONCAT('[', GROUP_CONCAT(
                JSON_OBJECT('waktu', waktu_id, 'ruang', ruang_id, 'priority', priority, 'reason', reason)
            ), ']')
            FROM reserved_slots WHERE dosen = p.dosen), '[]'
        ), ', ',
        '"preferred_slots": ', IFNULL(
            (SELECT CONCAT('[', GROUP_CONCAT(
                JSON_OBJECT('waktu', waktu_id, 'priority', priority_level)
            ), ']')
            FROM preferred_slots WHERE dosen = p.dosen), '[]'
        ), ', ',
        '"blocked_slots": ', IFNULL(
            (SELECT CONCAT('[', GROUP_CONCAT(
                JSON_OBJECT('waktu', waktu_id, 'reason', reason)
            ), ']')
            FROM blocked_slots WHERE dosen = p.dosen), '[]'
        ), ', ',
        '"flexible_slots": ', IFNULL(
            (SELECT CONCAT('[', GROUP_CONCAT(
                JSON_OBJECT('waktu', waktu_id, 'priority', priority_level)
            ), ']')
            FROM flexible_slots WHERE dosen = p.dosen), '[]'
        ),
    '}') as enhanced_preferences
FROM (SELECT DISTINCT dosen FROM preferensi_waktu_dosen) p;
*/

-- Query untuk scheduling analytics
/*
SELECT 
    w.hari,
    w.session_name,
    COUNT(sr.id) as total_classes,
    COUNT(DISTINCT sr.kuliah_id) as unique_courses,
    AVG(sr.fitness_score) as avg_fitness
FROM waktu2 w
LEFT JOIN schedule_results sr ON w.id = sr.waktu_id
GROUP BY w.id, w.hari, w.session_name
ORDER BY w.id;
*/