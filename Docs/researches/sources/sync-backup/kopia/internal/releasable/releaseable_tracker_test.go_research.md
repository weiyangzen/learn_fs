# sources/sync-backup/kopia/internal/releasable/releaseable_tracker_test.go

Purpose: validates releasable resource tracking behavior.

Important APIs/types/functions: `TestReleaseable`, `EnableTracking`, `Created`, `Released`, `Verify`, `Active`, and `DisableTracking`.

Control flow: enables a kind, creates and releases items, checks active maps and verification errors, and disables tracking.

State and persistence behavior: mutates package-global trackers, so cleanup is important for test isolation.

Dependencies and integration points: tests the public package from `releasable_test`.

Risks and test signals: should be run with race detector if resource tracking is used concurrently.
