# sources/user-network-fs/blobfuse2/cmd/unmount_test.go
## sources/user-network-fs/blobfuse2/cmd/unmount_test.go

Purpose: integration-oriented tests for mounting loopbackfs and unmounting via the Cobra command paths.

Important APIs/helpers: `unmountTestSuite`, `configUnMountLoopback`, `confFileUnMntTest`, `currentDir`, `SetupTest`, `cleanupTest`, and `TestUnMountCommand`. Tests use `executeCommandC` and reset root/mount/unmount flags.

Control flow: `TestUnMountCommand` creates a temporary loopback config and backing directory, then runs the suite. Individual tests invoke `../blobfuse2 mount`, wait, and then exercise `rootCmd unmount`: normal unmount, busy-directory failure followed by success after leaving the directory, wildcard unmount success/failure, shell completion returning mount points, lazy unmount through both `--lazy` and `-z` before/after the path, and unknown mount flags.

State and persistence: creates temporary mount directories, a temp config file, changes process working directory in busy-mount cases, and mutates real FUSE mount state through the built `../blobfuse2` binary. Sleeps are used to wait for mount/unmount state.

Dependencies/integration: requires a built binary at `../blobfuse2`, functioning FUSE/loopbackfs environment, fusermount tools, `/etc/mtab`, and permissions allowing mounts. Uses silent logger.

Risks: slow and environment-sensitive; CI without FUSE support or the expected binary will fail. Working-directory changes can leak if an assertion aborts before cleanup. Time-based waits can be flaky. Tests use global command state and flags.

Test signals: strong end-to-end coverage for unmount semantics, including lazy unmount and busy mount failure behavior, but it is not a pure unit test suite.
