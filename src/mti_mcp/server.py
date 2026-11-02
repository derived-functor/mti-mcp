"""Model Context Protocol server for the LMS MTI portal."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from mcp.server.fastmcp import FastMCP
from mti_api import MTIClient, to_dict


mcp = FastMCP("mti")
_client: MTIClient | None = None


def _get_client() -> MTIClient:
    """Create one authenticated client for the lifetime of the server."""

    global _client
    if _client is None:
        _client = MTIClient.from_env(
            base_url=os.environ.get("MTI_BASE_URL", "https://lms.mti.moscow"),
            session_path=os.environ.get(
                "MTI_SESSION_PATH",
                str(Path.home() / ".cache" / "mti-api" / "session.pickle"),
            ),
        )
    return _client


def _result(value: Any) -> Any:
    return to_dict(value)


def _download_dir() -> Path:
    destination = Path(
        os.environ.get("MTI_DOWNLOAD_DIR", str(Path.home() / "Downloads" / "mti"))
    ).expanduser()
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def _safe_filename(filename: str | None, fallback: str) -> str | None:
    if not filename:
        return None
    # The API returns filenames from the portal; only keep the basename when a
    # caller supplies one so a tool call cannot escape MTI_DOWNLOAD_DIR.
    value = Path(filename).name.strip()
    return value or fallback


@mcp.tool()
def get_user_summary() -> dict[str, Any]:
    """Return the authenticated student's short profile and group."""
    return _result(_get_client().get_user_summary())


@mcp.tool()
def get_profile(user_id: int | None = None) -> dict[str, Any]:
    """Return the student's full profile, optionally by LMS user ID."""
    return _result(_get_client().get_profile(user_id))


@mcp.tool()
def get_announcements() -> list[dict[str, Any]]:
    """List announcements from the LMS."""
    return _result(_get_client().get_announcements())


@mcp.tool()
def get_academic_schedule(
    date_from: str | None = None,
    date_to: str | None = None,
    my_schedule: int = 1,
    employee: str = "",
    group: str = "",
    discipline: str = "",
) -> list[dict[str, Any]]:
    """Return classroom lessons for the requested filters."""
    return _result(
        _get_client().get_academ_schedule(
            date_from=date_from,
            date_to=date_to,
            my_schedule=my_schedule,
            employee=employee,
            group=group,
            discipline=discipline,
        )
    )


@mcp.tool()
def get_webinar_schedule() -> list[dict[str, Any]]:
    """Return scheduled webinars and their links."""
    return _result(_get_client().get_webinar_schedule())


@mcp.tool()
def export_academic_schedule(
    date_from: str | None = None,
    date_to: str | None = None,
    my_schedule: int = 1,
) -> dict[str, Any]:
    """Export the academic schedule as XLSX into MTI_DOWNLOAD_DIR."""
    download = _get_client().export_academ_schedule_xlsx(
        date_from=date_from,
        date_to=date_to,
        my_schedule=my_schedule,
    )
    path = download.save(_download_dir())
    return {"path": str(path), "filename": download.filename, "content_type": download.content_type}


@mcp.tool()
def get_courses(semester: int | None = None) -> list[dict[str, Any]]:
    """Return courses, optionally limited to one semester."""
    return _result(_get_client().get_courses(semester=semester))


@mcp.tool()
def get_curriculum() -> list[dict[str, Any]]:
    """Return the student's curriculum."""
    return _result(_get_client().get_curriculum())


@mcp.tool()
def get_gradebook() -> list[dict[str, Any]]:
    """Return the student's grade book."""
    return _result(_get_client().get_gradebook())


@mcp.tool()
def get_tku() -> list[dict[str, Any]]:
    """Return current-control scores."""
    return _result(_get_client().get_tku())


@mcp.tool()
def get_course(course_id: int, url: str | None = None) -> dict[str, Any]:
    """Return detailed materials, events and results for one course."""
    return _result(_get_client().get_course(course_id, url=url))


@mcp.tool()
def get_finance() -> dict[str, Any]:
    """Return payments, receipts and finance details."""
    return _result(_get_client().get_finance())


@mcp.tool()
def get_documents() -> list[dict[str, Any]]:
    """Return the student's document tree without downloading files."""
    return _result(_get_client().get_documents())


@mcp.tool()
def download_document(url: str, filename: str | None = None) -> dict[str, Any]:
    """Download one document into MTI_DOWNLOAD_DIR and return its local path."""
    client = _get_client()
    parsed = urlparse(url)
    base = urlparse(client.base_url)
    if parsed.scheme not in ("http", "https") or parsed.netloc != base.netloc:
        raise ValueError("document URL must belong to the configured LMS host")
    download = client.download_document(url, filename=_safe_filename(filename, "document"))
    destination = _download_dir()
    path = download.save(destination)
    return {"path": str(path), "filename": download.filename, "content_type": download.content_type}


@mcp.tool()
def get_messages() -> list[dict[str, Any]]:
    """Return personal messages."""
    return _result(_get_client().get_messages())


@mcp.tool()
def get_notifications(archive: bool = False) -> list[dict[str, Any]]:
    """Return current notifications, or archived ones when requested."""
    return _result(_get_client().get_notifications(archive=archive))


def main() -> None:
    """Run the MCP server over stdio."""
    mcp.run()
