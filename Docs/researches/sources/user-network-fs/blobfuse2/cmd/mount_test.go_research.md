<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_test.go -->
# sources/user-network-fs/blobfuse2/cmd/mount_test.go

Purpose: broad unit/integration-style test suite for the main mount command, mount-all validation, fuse option parsing, cleanup-on-start, default config discovery, direct-IO behavior, and logging defaults.

Important APIs/types/functions: config fixtures `configMountTest`, `configPriorityTest`, `configDirectIOTest`; `mountTestSuite`; `SetupSuite`, `SetupTest`, `cleanupTest`; `executeCommandC`; `resetCLIFlags`; `viper.Reset`; `ignoreFuseOptions`; `updateCliParams`; `mountOptions.validate`; `tempCacheCleanup`; and `TestMountCommand`.

Control flow: the suite creates temporary config files and mount directories, invokes `rootCmd mount` or `rootCmd mount all`, and generally expects failure after validation or pipeline initialization because real storage/FUSE is not available. It verifies error text for missing directories, non-empty mount points, empty mount path, unsupported config type, missing config, missing default config, wrong component order, invalid log level, v1 compatibility flags, direct-IO/kernel-cache conflicts, invalid fuse options, invalid uid/gid/umask, unknown flags, ignored fuse options, CLI param replacement, mount option validation, cache cleanup for file_cache/block_cache/xload, and default goroutine-id behavior for log levels.

State/persistence behavior: creates/removes temp mount dirs, temp configs, default `config.yaml`, cache directories and files under `/tmp`, and resets global default work/log paths. It mutates global `options`, viper state, and config keys and must reset them to avoid cross-test contamination.

Dependencies/integration: depends on many shared helpers from the command test harness, common filesystem helpers, component pipeline validation, and local OS behavior for directory emptiness and path expansion. Some tests intentionally proceed to pipeline initialization and assert failure rather than mounting.

Risks/test signals: several assertions rely on exact error fragments. The suite does not validate successful live mounts, daemon behavior, or Azure connectivity, but it provides strong regression coverage for preflight validation and option translation. Global-state resets are essential; adding tests without cleanup can create flakes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_test.go -->
