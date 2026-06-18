## sources/sync-backup/syncthing/lib/events/debug.go

Purpose: Defines event package debug logger adapter.

Important APIs/types/functions: Package variable `dl = slogutil.NewAdapter("Event generation and logging")`.

Control flow: None beyond package initialization.

State and persistence: Process-global logger adapter only.

Dependencies and integration points: Used by event logger and subscription methods for diagnostics.

Risks: None beyond logger naming.

Test signals: Compile-time use validates symbol.
