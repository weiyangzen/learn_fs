## sources/sync-backup/syncthing/lib/model/sharedpullerstate_test.go

Purpose: regression test for creating temporary puller files inside a read-only directory on Syncthing's fake filesystem.

Important test: `TestReadOnlyDir` creates a fake filesystem directory with mode `0555`, constructs a minimal `sharedPullerState` pointing to a temp file inside it, calls `tempFile`, asserts a non-nil descriptor, then final-closes the state.

Control flow and state: the test exercises `inWritableDir` through `sharedPullerState.tempFile`, confirming that directory permissions can be temporarily handled for temp-file creation. It also verifies `fail(nil)` is a no-op and `finalClose` can clean up the opened writer.

Dependencies and integration points: uses fake filesystem and random path roots. It is focused on permission handling in the puller temp-file path.

Risks: fake filesystem behavior may not model all host filesystem permission nuances, especially Windows ACLs or network filesystems.

Test signals: narrow but useful coverage of temp file creation under restrictive parent permissions.
