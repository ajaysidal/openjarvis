"""Data source connectors for Deep Research."""

from silas.connectors._stubs import (
    Attachment,
    BaseConnector,
    Document,
    SyncStatus,
)
from silas.connectors.store import KnowledgeStore

__all__ = ["Attachment", "BaseConnector", "Document", "KnowledgeStore", "SyncStatus"]

# Auto-register built-in connectors
import silas.connectors.obsidian  # noqa: F401

try:
    import silas.connectors.gmail  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.gmail_imap  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.gdrive  # noqa: F401
except ImportError:
    pass  # httpx may not be installed

try:
    import silas.connectors.notion  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.granola  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.gcontacts  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.imessage  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.apple_notes  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.apple_music  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.apple_contacts  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.apple_calendar  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.slack_connector  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.outlook  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.imap  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.gcalendar  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.dropbox  # noqa: F401
except ImportError:
    pass  # httpx may not be installed

try:
    import silas.connectors.whatsapp  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.oura  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.apple_health  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.strava  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.spotify  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.google_tasks  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.weather  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.github_notifications  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.github  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.hackernews  # noqa: F401
except ImportError:
    pass

try:
    import silas.connectors.news_rss  # noqa: F401
except ImportError:
    pass
