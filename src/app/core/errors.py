class RepositoryError(Exception):
    """Base error class for repository related errors."""

    pass


class NotFoundError(RepositoryError):
    """Raised when an entity is not found in the repository."""

    pass


class DuplicateEntityError(RepositoryError):
    """Raised when trying to create an entity that already exists."""

    pass
