CREATE TABLE `logs` (
`log_id` INT NOT NULL AUTO_INCREMENT,
`log_dir` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
`log_name` VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
PRIMARY KEY (`log_id`)
) ENGINE = ROCKSDB;

INSERT INTO logs (log_dir, log_name) SELECT log_dir, log_name FROM (SELECT DISTINCT log_dir, log_name FROM chat) ch LEFT JOIN logs USING (log_dir, log_name) WHERE log_id IS NULL;

