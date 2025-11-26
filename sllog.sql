-- This is the only table used by the script

CREATE TABLE IF NOT EXISTS `chat` (
  `id` int(11) NOT NULL,
  `log_dir` varchar(255) COLLATE utf8mb4_bin NOT NULL,
  `log_name` varchar(255) COLLATE utf8mb4_bin NOT NULL,
  `bytepos_end` int(11) NOT NULL,
  `timestamp_raw` char(16) COLLATE utf8mb4_bin NOT NULL,
  `timestamp_parsed` datetime NOT NULL,
  `display_name` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `user_name` varchar(64) COLLATE utf8mb4_bin DEFAULT NULL,
  `type` tinyint(4) NOT NULL,
  `message` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- Remove fulltext index if you don't need it for external tools

ALTER TABLE `chat`
 ADD PRIMARY KEY (`id`), ADD KEY `log_dir_name` (`log_dir`(191),`log_name`(191),`id`), ADD KEY `chat_username` (`user_name`,`id`), ADD FULLTEXT KEY `fts` (`message`);

-- For fast lookup of repeated messages and usernames, not used by the script

DELIMITER //
CREATE TRIGGER `chat_after_insert` AFTER INSERT ON `chat`
 FOR EACH ROW BEGIN
INSERT INTO `chat_hashcounts` (hash, count, message_id) VALUES (UNHEX(SHA2(NEW.message, 256)), 1, NEW.id) ON DUPLICATE KEY UPDATE count = count + 1;
IF NEW.user_name IS NOT NULL THEN
INSERT INTO `chat_usernames` (user_name, count) VALUES (NEW.user_name, 1) ON DUPLICATE KEY UPDATE count = count + 1;
ELSEIF NEW.display_name IS NOT NULL THEN
INSERT INTO `chat_displaynames` (display_name, count) VALUES (NEW.display_name, 1) ON DUPLICATE KEY UPDATE count = count + 1;
END IF;
END
//
DELIMITER ;

CREATE TABLE IF NOT EXISTS `chat_displaynames` (
  `display_name` varchar(191) COLLATE utf8mb4_bin NOT NULL,
  `count` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS `chat_hashcounts` (
  `hash` binary(32) NOT NULL,
  `count` int(11) NOT NULL,
  `message_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS `chat_usernames` (
  `user_name` varchar(64) COLLATE utf8mb4_bin NOT NULL,
  `count` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

ALTER TABLE `chat_displaynames`
 ADD PRIMARY KEY (`display_name`), ADD KEY `count` (`count`);
ALTER TABLE `chat_hashcounts`
 ADD PRIMARY KEY (`hash`), ADD KEY `count` (`count`);
ALTER TABLE `chat_usernames`
 ADD PRIMARY KEY (`user_name`), ADD KEY `count` (`count`);

CREATE TABLE IF NOT EXISTS `logs` (
  `log_id` int(11) NOT NULL AUTO_INCREMENT,
  `log_dir` varchar(255) NOT NULL,
  `log_name` varchar(255) NOT NULL,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

