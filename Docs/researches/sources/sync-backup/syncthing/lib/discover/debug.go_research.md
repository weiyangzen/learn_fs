## sources/sync-backup/syncthing/lib/discover/debug.go

Purpose: Defines discovery package debug logger adapter.

Important APIs/types/functions: Package variable `l = slogutil.NewAdapter("Remote device discovery")`.

Control flow: None beyond initialization.

State and persistence: Process-global logger adapter only.

Dependencies and integration points: Used by local/global/manager discovery files for debug diagnostics.

Risks: None beyond logger naming.

Test signals: Compile-time use validates symbol.
