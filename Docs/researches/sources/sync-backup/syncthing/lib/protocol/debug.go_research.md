## sources/sync-backup/syncthing/lib/protocol/debug.go

Purpose: defines the protocol package logging adapter.

Important API: variable `l = slogutil.NewAdapter("The BEP protocol")`.

Control flow and state: package initialization only.

Dependencies and integration points: used by protocol connection internals for debug logging.

Risks: none beyond logging category naming.

Test signals: no direct tests.
