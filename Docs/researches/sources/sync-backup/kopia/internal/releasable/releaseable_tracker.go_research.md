# sources/sync-backup/kopia/internal/releasable/releaseable_tracker.go

Purpose: provides optional process-wide tracking for resources that must be released, capturing allocation stack traces for leak diagnostics.

Important APIs/types/functions: `ItemKind`, `Created`, `Released`, `Active`, `Verify`, `EnableTracking`, `DisableTracking`, and `perKindTracker`.

Control flow: enabling a kind installs a tracker. `Created` records `debug.Stack()` under an item ID, `Released` deletes it, `Active` clones all maps, and `Verify` formats any remaining active items into an error.

State and persistence behavior: global in-memory maps protected by mutexes; tracking is disabled per kind by removing its tracker.

Dependencies and integration points: test and debug-only consumers can enable tracking around resource lifecycles.

Risks and test signals: globals can leak between tests if not disabled, and item IDs must be comparable. Tests cover enable/create/release/verify lifecycle.
