# sources/sync-backup/syncthing/lib/connections/debug.go

## sources/sync-backup/syncthing/lib/connections/debug.go

Purpose: Provides the package-local logging adapter for connection handling.

Important APIs/types/functions: Declares `l = slogutil.NewAdapter("Connection handling")`.

Control flow and state: Static package initialization only.

Dependencies and integration: Used throughout connection services, dialers, listeners, LAN checking, and limiter code for debug logging.

Risks and test signals: Minimal logic risk; logging category stability affects diagnostics. No direct tests.
