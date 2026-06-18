# Research: sources/sync-backup/syncthing/test/conflict_test.go

## sources/sync-backup/syncthing/test/conflict_test.go

Purpose: integration tests for conflict creation and resolution across two Syncthing peers.

Important APIs/functions: `TestConflictsDefault`, `TestConflictsInitialMerge`, `TestConflictsIndexReset`, and `TestConflictsSameContent`.

Control flow: tests clean data/index directories, create divergent file states, start h1/h2 instances, resume devices, force or delay scans, pause/resume peer links to create simultaneous edits or edit/delete conflicts, then use `rc.AwaitSync`, glob checks, content checks, and directory-content comparison.

State and persistence: uses `s1`, `s2`, and `h1/h2` index directories. Conflict artifacts are files containing `sync-conflict` in the name. Index reset test deliberately deletes `h2/index*`.

Dependencies and integration: `lib/rc` process API, local Syncthing instances, filesystem mtimes, helper functions from the integration suite. Risks include timing sensitivity, conflict filename expectations, and index-reset behavior changing with database logic. Test signals assert conflict counts, propagated contents, and same-content non-conflict handling.
