from dataclasses import dataclass, field
import uuid


@dataclass
class Movie:
    """Фильмы"""
    title: str
    plot: str
    imdb_rating: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Genre:
    """Жанры."""
    name: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class Person:
    """Люди."""
    name: str
    role: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class MovieGenre:
    """Связь фильмов и жанров."""
    movie_id: uuid.UUID = field(default_factory=uuid.uuid4)
    genre_id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class MoviePerson:
    """Связь фильмов и людей"""
    role: str
    movie_id: uuid.UUID = field(default_factory=uuid.uuid4)
    person_id: uuid.UUID = field(default_factory=uuid.uuid4)