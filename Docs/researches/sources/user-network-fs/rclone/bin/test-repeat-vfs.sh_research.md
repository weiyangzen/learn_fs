# sources/user-network-fs/rclone/bin/test-repeat-vfs.sh

Purpose: convenience wrapper that repeatedly runs selected VFS and mount-related test directories through `bin/test-repeat.sh`, defaulting to 100 iterations and enabling race detector plus `cmount` tags.

State changes are compiled test binaries and failure logs in each test directory. Dependencies are bash, realpath, Go test, race support, and mount/cmount build prerequisites. Risks include long runtime, large log buildup on repeated failures, and platform-specific cmount/FUSE requirements. Test signal is repeated successful test execution with intermittent failures retained as logs.
