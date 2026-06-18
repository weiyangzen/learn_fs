## sources/sync-backup/syncthing/lib/dialer/debug.go

Purpose: Defines the dialer package debug logger adapter.

Important APIs/types/functions: Package variable `l = slogutil.NewAdapter("Dialing connections")`.

Control flow: None beyond package initialization.

State and persistence: Process-global logger adapter only.

Dependencies and integration points: Used throughout dialer internals for proxy/fallback/socket diagnostic logging.

Risks: None beyond consistent logger naming.

Test signals: No tests needed; compile-time use validates symbol.
