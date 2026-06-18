<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_dir_plus_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/read_dir_plus_test.go

Purpose: validates FUSE `ReadDirPlus` behavior, including entry attributes, dentry/inode attribute caching, implicit directories, symlinks, and local-only files.

Important APIs/types/functions: testify suites `ReadDirPlusTest` and `LocalFileEntriesReadDirPlusTest`; `fusetesting.ReadDirPlusPicky`; mount flag `EnableReaddirplus`; server fields `ImplicitDirectories`, `InodeAttributeCacheTTL`, and `cfg.FileSystem.ExperimentalEnableDentryCache`.

Control flow: suite setup enables readdirplus and dentry cache, creates remote objects and local symlinks/files, then calls `ReadDirPlusPicky` against `mntDir`. The test checks sorted entries and per-entry mode, size, and directory status. A cache test reads directory attributes, mutates the backing GCS object, stats before and after TTL expiry, and expects stale then refreshed attributes.

State and persistence behavior: persistent data is fake GCS content plus local unsynced file state. In-memory state under test includes inode attribute cache and dentry cache entries populated by `ReadDirPlus`. Local-only entries must appear even before they are persisted to GCS.

Dependencies and integration points: exercises `fileSystem.ReadDirPlus`, directory handle listing, local inode merging with GCS entries, symlink creation via `CreateSymlink`, inode attribute cache TTL, and dentry cache integration.

Risks: cache TTL tests rely on wall-clock sleeps, which can be timing-sensitive. Attribute parity between `ReadDirPlus` and later `Stat` is critical because kernels can use readdirplus as a metadata prefetch path.

Test signals: empty directory, mixed file/explicit dir/implicit dir/symlink listing, stat-after-readdirplus cache consistency, local-only file listing, and merged local plus GCS entry listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_dir_plus_test.go -->
