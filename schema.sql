CREATE TABLE `movie` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `movie_id` varchar(20) DEFAULT NULL,
  `title` varchar(200) DEFAULT NULL,
  `genres` varchar(100) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `imdb` varchar(50) DEFAULT NULL,
  `tmdb` varchar(50) DEFAULT NULL,
  `tags` text,
  `related_films` varchar(200) DEFAULT NULL,
  `user_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rating` (`rating`)
) ENGINE=InnoDB AUTO_INCREMENT=96885 DEFAULT CHARSET=utf8;