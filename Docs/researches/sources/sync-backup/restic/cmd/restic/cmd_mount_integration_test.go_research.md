# sources/sync-backup/restic/cmd/restic/cmd_mount_integration_test.go

Purpose: FUSE integration coverage for `restic mount` and local repository/mountpoint overlap validation.

Important APIs/types/functions: `waitForMount`; `testRunMount`; `testRunUmount`; `checkSnapshots`; `TestMount`; `TestCheckMountpointOverlap`; `TestCheckMountpointOverlapSymlink`; `TestMountSameTimestamps`.

Control flow and state: tests run mount in a goroutine, poll for the virtual `snapshots` directory, inspect virtual snapshot names including `latest`, then unmount and wait. Backup sequences create zero, one, two, and three snapshots to verify virtual directory counts. Overlap tests call `checkMountpointOverlap` directly with equal, nested, sibling, prefix, and symlink paths.

Dependencies and integration points: requires `rtest.RunFuseTest`, anacrolix fuse unmount, debug logging, snapshot loading, and integration environment helpers.

Risks: timing and OS FUSE availability can make tests flaky or skipped. Virtual snapshot naming is tied to RFC3339 defaults and duplicate timestamp suffixing.

Test signals: validates the core mount lifecycle and the deadlock-prevention overlap guard.
