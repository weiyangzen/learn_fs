<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/fs_test.go

Purpose: provides the shared FUSE integration-test harness for `internal/fs`, including mount setup/teardown, fake bucket manager, default server configuration, helper object creation, and common file utilities.

Important APIs/types/functions: `TestFS`, package `init` signal handler, constants `filePerms`, `dirPerms`, `RenameDirLimit`, `SequentialReadSizeMb`, struct `fsTest`, globals `mntDir`, `ctx`, `mfs`, `mtimeClock`, `cacheClock`, `bucket`, `buckets`, `bucketType`, `defaultFileCacheConfig`, `SetUpTestSuite`, `TearDownTestSuite`, `TearDown`, object helpers, `getFileNames`, `randBytes`, `readRange`, `currentUid`, `currentGid`, `fakeBucketManager`, and its `SetUpBucket`.

Control flow: setup initializes clocks, chooses single-bucket or all-buckets mode, creates fake bucket manager and default config, fills ownership/permission fields, creates a temp mount directory, builds a server with `fs.NewServer`, configures logging, and mounts FUSE. Teardown retries unmount on resource-busy, joins the mounted filesystem, removes the mount point, resets global bucket state, and per-test cleanup removes mount contents and closes open files.

State and persistence: test state spans package globals, mounted FUSE server, fake buckets, simulated cache clock, temp mount directory, and open file handles. Data persists in fake bucket memory during a suite and is cleaned between tests where possible.

Dependencies and integration points: integrates `fs.NewServer`, `fuse.Mount`, `fusetesting`, fake storage, `gcsx.NewSyncerBucket`, permissions, metrics/tracing noops, logger, locker debugging, and ogletest. Other test files embed `fsTest`.

Risks: package-level globals make suites order-sensitive unless reset carefully. Real FUSE mount support is required. Signal handling stops tests after SIGINT. Cleanup ignores some removal errors intentionally, which can mask leftover state in unusual cases.

Test signals: this file is infrastructure rather than assertions, but it establishes representative default config: metadata cache defaults, new reader enabled, unlimited file cache size, fixed file/dir perms, rename limit, and sequential read size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_test.go -->
