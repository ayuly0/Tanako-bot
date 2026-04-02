class TanakoError(Exception):
    """Base Exception for all Tanako-bot related errors."""
    pass

class DatabaseError(TanakoError):
    """Raised when there's an error in the database layer."""
    pass

class EntityNotFoundError(DatabaseError):
    """Raised when an entity is not found in the database."""
    pass

class ConfigurationError(TanakoError):
    """Raised when there's a configuration-related error."""
    pass

class PermissionDeniedError(TanakoError):
    """Raised when a user lacks required permissions."""
    pass

class IntegrationError(TanakoError):
    """Raised when external integration (Discord API, Webhooks) fails."""
    pass
