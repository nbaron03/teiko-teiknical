CREATE TABLE subjects (
    subject_id  TEXT PRIMARY KEY,
    project     TEXT NOT NULL,          
    condition   TEXT NOT NULL,           
    age         INTEGER NOT NULL,
    sex         TEXT NOT NULL,           
    treatment   TEXT NOT NULL,           
    response    TEXT                     
);

CREATE TABLE samples (
    sample_id                  TEXT PRIMARY KEY,
    subject_id                 TEXT NOT NULL,
    sample_type                TEXT NOT NULL,
    time_from_treatment_start  INTEGER NOT NULL,
    b_cell                     INTEGER NOT NULL,
    cd8_t_cell                 INTEGER NOT NULL,
    cd4_t_cell                 INTEGER NOT NULL,
    nk_cell                    INTEGER NOT NULL,
    monocyte                   INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);