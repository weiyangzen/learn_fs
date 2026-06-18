# sources/user-network-fs/go-fuse/fs/loopback_test.go

Purpose: cross-platform loopback tests for rename exchange and using loopback roots below a larger synthetic root.

Important tests: `TestRenameExchange` creates two files, performs `RENAME_EXCHANGE`, verifies backing stat metadata swaps, and checks go-fuse inode tree stable attrs update for root and nested paths. `TestLoopbackNonRoot` mounts a synthetic root containing two different loopback roots, verifies reads through a submount, expects `EXDEV` for cross-root renames, and succeeds for rename within the same loopback root.

State/dependencies: real temp backing dirs, FUSE mounts, renameat helper, syscall stats.

Risks/test signals: covers hard namespace integration between `LoopbackNode` and in-memory parent roots. Rename exchange support may be skipped if unsupported.
