-- SQL script that creates an index
-- idx_name_first_score on the table names
CREATE INDEX idx_name_first ON names(name(1));
