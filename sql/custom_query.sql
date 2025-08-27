WITH movies AS (
	SELECT id,
		imdb_id,
		title,
		original_title,
		tagline,
		overview,
		runtime,
		status,
		release_date,
		original_language,
		popularity,
		vote_average,
		vote_count,
		backdrop_path,
		poster_path,
		belongs_to_collection,
		publication_id,
		genre_ids.genre_id,
        spoken_languages,
        origin_country
	FROM movie_details
	JOIN JSON_TABLE(
		genres,
		'$[*]' COLUMNS (genre_id VARCHAR(50) PATH '$')
	) AS genre_ids
),
movies_with_genre AS (
	SELECT m.id,
		m.imdb_id,
		m.title,
		m.original_title,
		m.tagline,
		m.overview,
		m.runtime,
		m.status,
		m.release_date,
		g.name AS genre,
		m.original_language,
		m.spoken_languages,
		m.origin_country,
		m.popularity,
		m.vote_average,
		m.vote_count,
		CONCAT('https://image.tmdb.org/t/p/original', m.backdrop_path) AS backdrop_path,
		CONCAT('https://image.tmdb.org/t/p/original', m.poster_path) AS poster_path,
		m.belongs_to_collection,
		m.publication_id
	FROM movies m
    JOIN genres g
		ON m.genre_id = g.id
)
SELECT * FROM movies_with_genre
;