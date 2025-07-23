-- ADSUN Process Management Database Schema
-- Databázová štruktúra pre systém riadenia procesov

-- Tabuľka pre hlavné procesy
CREATE TABLE processes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- obchod, výroba, administratíva, IT, HR
    trigger_type VARCHAR(255) NOT NULL, -- čo proces spustí
    owner VARCHAR(255) NOT NULL, -- zodpovedná osoba
    frequency VARCHAR(100) NOT NULL, -- denne/týždenne/mesačne
    duration_minutes INTEGER, -- priemerné trvanie v minútach
    priority VARCHAR(20) NOT NULL, -- vysoká/stredná/nízka
    volume_per_period INTEGER, -- koľko položiek za obdobie
    success_criteria TEXT, -- kritériá úspechu
    common_problems TEXT, -- časté problémy
    automation_readiness INTEGER CHECK(automation_readiness >= 1 AND automation_readiness <= 5),
    tags TEXT, -- JSON array kľúčových slov
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Tabuľka pre kroky procesov
CREATE TABLE process_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    responsible_person VARCHAR(255) NOT NULL,
    system_tool VARCHAR(255), -- používaný systém/nástroj
    input_data TEXT, -- vstupné dáta (JSON)
    action_details TEXT NOT NULL, -- čo sa presne deje
    output_data TEXT, -- výstupné dáta (JSON)
    decision_logic TEXT, -- rozhodovacia logika
    estimated_time_minutes INTEGER,
    is_automated BOOLEAN DEFAULT 0,
    automation_potential INTEGER CHECK(automation_potential >= 1 AND automation_potential <= 5),
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);

-- Tabuľka pre súvislosti medzi procesmi
CREATE TABLE process_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_a_id INTEGER NOT NULL,
    process_b_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- 'predecessor', 'successor', 'related', 'dependency'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_a_id) REFERENCES processes(id) ON DELETE CASCADE,
    FOREIGN KEY (process_b_id) REFERENCES processes(id) ON DELETE CASCADE
);

-- Tabuľka pre zdroje a nástroje
CREATE TABLE process_resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    resource_type VARCHAR(100) NOT NULL, -- 'system', 'document', 'template', 'external_service'
    resource_name VARCHAR(255) NOT NULL,
    resource_url VARCHAR(500),
    description TEXT,
    is_critical BOOLEAN DEFAULT 0,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);

-- Tabuľka pre históriu dokumentovania
CREATE TABLE documentation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_id INTEGER NOT NULL,
    documented_by VARCHAR(255) NOT NULL,
    session_notes TEXT,
    completeness_score INTEGER CHECK(completeness_score >= 1 AND completeness_score <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (process_id) REFERENCES processes(id) ON DELETE CASCADE
);

-- Indexy pre rýchlejšie vyhľadávanie
CREATE INDEX idx_processes_category ON processes(category);
CREATE INDEX idx_processes_priority ON processes(priority);
CREATE INDEX idx_processes_owner ON processes(owner);
CREATE INDEX idx_process_steps_process_id ON process_steps(process_id);
CREATE INDEX idx_process_relationships_process_a ON process_relationships(process_a_id);
CREATE INDEX idx_process_relationships_process_b ON process_relationships(process_b_id);

-- Trigre pre automatické aktualizovanie timestampov
CREATE TRIGGER update_processes_timestamp 
    AFTER UPDATE ON processes
BEGIN
    UPDATE processes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END; 