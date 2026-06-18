## sources/sync-backup/syncthing/lib/osutil/lowprio_noop.go

Purpose: iOS no-op implementation of priority lowering.

Important API: `SetLowPriority` returns nil.

Control flow and state: none.

Dependencies and integration points: selected by iOS build tags to satisfy the cross-platform API.

Risks: callers may believe priority was lowered when the platform cannot do it; this is intentional.

Test signals: no direct tests.
