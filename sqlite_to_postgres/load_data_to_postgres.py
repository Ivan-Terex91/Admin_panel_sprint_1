from my_dataclasses import Person, Genre, Movie, MoviePerson, MovieGenre
import psycopg2.extras

psycopg2.extras.register_uuid()


class PostgresSaver:
    """Класс загрузки данных в Postgres."""

    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.movies_from_sqlite = []

    def load_movie(self, single_movie: dict) -> str:
        """Загрузка фильма."""

        movie = Movie(title=single_movie.get("title"), plot=single_movie.get("description"),
                      imdb_rating=single_movie.get("imdb_rating"))
        data = (movie.id, movie.title, movie.plot, movie.imdb_rating)
        self.cursor.execute(f"""
                 INSERT INTO content.movie(id, title, plot, imdb_rating)
                 VALUES (%s, %s, %s, %s)
                 ON CONFLICT (id) DO NOTHING
                 RETURNING content.movie.id;
                 """, data)
        movie_returning_id = self.cursor.fetchone()
        movie_id = movie_returning_id[0] if movie_returning_id else movie.id
        return movie_id

    def load_genre_and_movie_genre(self, single_movie, movie_id):
        """Загрузка жанра и заполнение таблицы movie_genre."""

        genres = single_movie.get("genre")
        for genre in genres:
            _genre = Genre(name=genre)
            data = (_genre.id, _genre.name)
            self.cursor.execute(f"""
                WITH query_sel AS (
                    SELECT content.genre.id FROM content.genre
                    WHERE content.genre.name = %s
                ), query_ins AS (
                    INSERT INTO content.genre(id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                )
    
                SELECT %s as id FROM query_ins
                UNION ALL
                SELECT id AS id from query_sel;
            """, (_genre.name, *data, _genre.id))
            genre_id = self.cursor.fetchone()[0]

            movie_genre = MovieGenre(movie_id=movie_id, genre_id=genre_id)
            data = (movie_genre.movie_id, movie_genre.genre_id)
            self.cursor.execute(f"""
                                INSERT INTO content.movie_genre(movie_id, genre_id)
                                VALUES (%s, %s)
                                ON CONFLICT ON CONSTRAINT movie_genre_unique DO NOTHING
                """, data)

    def load_person_and_movie_person(self, single_movie: dict, movie_id):
        """Загрузка людей и заполнение таблицы movie_person."""

        person_list = single_movie.get("persons")
        for person in person_list:
            _person = Person(name=person[0], role=person[1])
            if not _person.name:
                continue
            data = (_person.id, _person.name)
            self.cursor.execute(f"""
                WITH query_sel AS (
                    SELECT content.person.id FROM content.person
                    WHERE content.person.name = %s
                    ), query_ins AS (
                    INSERT INTO content.person(id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                )

                SELECT %s as id FROM query_ins
                UNION ALL
                SELECT id AS id from query_sel;
                """, (_person.name, *data, _person.id))
            person_id = self.cursor.fetchone()[0]

            movie_person = MoviePerson(movie_id=movie_id, person_id=person_id, role=_person.role)
            data = (movie_person.movie_id, movie_person.person_id, movie_person.role)
            self.cursor.execute(f"""
                               INSERT INTO content.movie_person(movie_id, person_id, role)
                               VALUES (%s, %s, %s)
                               ON CONFLICT ON CONSTRAINT movie_person_unique DO NOTHING
               """, data)

    def save_all_data(self, movies_from_sqlite):
        """Загрузка всех фильмов."""
        self.movies_from_sqlite = movies_from_sqlite

        for movie in self.movies_from_sqlite:
            movie_id = self.load_movie(movie)
            self.load_genre_and_movie_genre(movie, movie_id)
            self.load_person_and_movie_person(movie, movie_id)
