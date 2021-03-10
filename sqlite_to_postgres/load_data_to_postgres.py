import my_dataclasses


class PostgresSaver:
    """Класс загрузки данных в Postgres."""

    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()
        self.movies_from_sqlite = []

    def load_movie(self, single_movie: dict) -> str:
        """Загрузка фильма."""

        movie = my_dataclasses.Movie(title=single_movie.get("title"), plot=single_movie.get("description"),
                                     imdb_rating=single_movie.get("imdb_rating"))

        data = (str(movie.id), movie.title, movie.plot, movie.imdb_rating)

        self.cursor.execute(f"""
                                 SELECT content.movie.id FROM content.movie
                                 WHERE content.movie.id = %s;
                                 """, (str(movie.id),))
        movie_returning_id = self.cursor.fetchone()

        if not movie_returning_id:
            self.cursor.execute(f"""
                     INSERT INTO content.movie(id, title, plot, imdb_rating)
                     VALUES (%s, %s, %s, %s)
                     ON CONFLICT (id) DO NOTHING
                     RETURNING content.movie.id;
                     """, data)
            movie_returning_id = self.cursor.fetchone()
        movie_id = movie_returning_id[0]

        return movie_id

    def load_genre_and_movie_genre(self, single_movie, movie_id):
        """Загрузка жанра и заполнение таблицы movie_genre."""

        genres = single_movie.get("genre")
        for genre in genres:
            _genre = my_dataclasses.Genre(name=genre)
            data = (str(_genre.id), _genre.name)
            self.cursor.execute(f"""
                                SELECT content.genre.id FROM content.genre
                                WHERE content.genre.name = %s;
                                """, (_genre.name,))
            genre_returning_id = self.cursor.fetchone()

            if not genre_returning_id:
                self.cursor.execute(f"""
                    INSERT INTO content.genre(id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING content.genre.id;
                    """, data)
                genre_returning_id = self.cursor.fetchone()
            genre_id = genre_returning_id[0]

            movie_genre = my_dataclasses.MovieGenre(movie_id=movie_id, genre_id=genre_id)
            data = (str(movie_genre.movie_id), str(movie_genre.genre_id))
            self.cursor.execute(f"""
                                INSERT INTO content.movie_genre(movie_id, genre_id)
                                VALUES (%s, %s)
                                ON CONFLICT ON CONSTRAINT movie_genre_unique DO NOTHING
                """, data)

    def load_person_and_movie_person(self, single_movie: dict, movie_id):
        """Загрузка людей и заполнение таблицы movie_person."""

        person_list = single_movie.get("persons")
        for person in person_list:
            _person = my_dataclasses.Person(name=person[0], role=person[1])
            if not _person.name:
                continue
            data = (str(_person.id), _person.name)
            self.cursor.execute(f"""
                                   SELECT content.person.id FROM content.person
                                   WHERE content.person.name = %s;
                               """, (_person.name,))
            person_returning_id = self.cursor.fetchone()

            if not person_returning_id:
                self.cursor.execute(f"""
                               INSERT INTO content.person(id, name)
                               VALUES (%s, %s)
                               ON CONFLICT (name) DO NOTHING
                               RETURNING content.person.id;
                               """, data)
                person_returning_id = self.cursor.fetchone()
            person_id = person_returning_id[0]

            movie_person = my_dataclasses.MoviePerson(movie_id=movie_id, person_id=person_id, role=_person.role)
            data = (str(movie_person.movie_id), str(movie_person.person_id), movie_person.role)
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
