"""Shared config — resolve Obsidian vault + paths from environment.

Set these env vars before running any script:
  OBSIDIAN_VAULT  (required) = absolute path to your Obsidian vault root
  DOWNLOADS_DIR   (optional) = browser Downloads folder (default: ~/Downloads)

PowerShell:  $env:OBSIDIAN_VAULT = 'C:\\path\\to\\vault'
bash/zsh:    export OBSIDIAN_VAULT=/path/to/vault
"""
import os
from pathlib import Path


def vault() -> Path:
    v = os.environ.get("OBSIDIAN_VAULT")
    if not v:
        raise SystemExit(
            "ERROR: set OBSIDIAN_VAULT to your Obsidian vault root first.\n"
            "  PowerShell:  $env:OBSIDIAN_VAULT = 'C:\\path\\to\\vault'\n"
            "  bash/zsh:    export OBSIDIAN_VAULT=/path/to/vault"
        )
    p = Path(v)
    if not p.exists():
        raise SystemExit(f"ERROR: OBSIDIAN_VAULT does not exist: {p}")
    return p


def archive() -> Path:
    """Where raw transcripts are written."""
    return vault() / "_archive" / "conversations-raw" / "youtube"


def attachments() -> Path:
    """Where captured images are stored (Obsidian `![[...]]` resolves by filename)."""
    return vault() / "_attachments"


def downloads() -> Path:
    return Path(os.environ.get("DOWNLOADS_DIR") or (Path.home() / "Downloads"))
