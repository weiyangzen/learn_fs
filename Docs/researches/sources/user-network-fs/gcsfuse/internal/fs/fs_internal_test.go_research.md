<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_internal_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/fs_internal_test.go

Purpose: unit-tests the internal file-cache disk block-size selection helper.

Important APIs/types/functions: `TestCacheDirVolumeBlockSize`, `cacheDirVolumeBlockSize`, `cfg.FileCacheConfig.ExperimentalDisableSizeCalculationFix`, `cfg.FileCacheConfig.ExperimentalEnableChunkCache`, and `diskutil.GetVolumeBlockSize`.

Control flow: the test creates a temporary directory, records the actual volume block size, then runs a table of configs. With the size calculation fix enabled and sparse/chunk cache disabled, the helper should return the real volume block size. When the fix is explicitly disabled, or sparse/chunk cache is enabled, it should return `1`.

State and persistence: uses a temporary directory only. No persistent state.

Dependencies and integration points: depends on the unexported helper in `fs.go`, `cfg`, `diskutil`, and `testify/assert`. This helper feeds file-cache size accounting in `createSingleMountFileCacheHandler` and downloader/cache handler construction.

Risks: the expected real block size is platform/filesystem dependent but read from the same directory immediately before assertions, reducing brittleness. The test does not verify logging or downstream cache-size accounting, only the branch decision.

Test signals: protects the compatibility behavior that disables block-size-based size accounting for sparse/chunk cache mode or when the experimental disable flag is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/fs_internal_test.go -->
