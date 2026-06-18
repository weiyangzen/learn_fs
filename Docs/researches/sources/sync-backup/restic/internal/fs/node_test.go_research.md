# sources/sync-backup/restic/internal/fs/node_test.go

Purpose: Cross-platform tests and benchmark for node conversion and metadata restore.

Important APIs: `BenchmarkNodeFromFileInfo`, `nodeTests`, `TestNodeRestoreAt`, `AssertFsTimeEqual`, and `TestNodeRestoreMetadataError`.

Control flow and state: Test nodes cover files, dirs, symlinks, setuid/setgid/sticky modes, repeated existing names, and xattrs. Each node is created, metadata is restored, then read back through `NewLocal().OpenFile(...).ToNode`.

Dependencies and integration: Exercises `NodeCreateAt`, `NodeRestoreMetadata`, xattr filters, timestamp restore, chmod, lchown, and node equality.

Risks: Platform differences are explicitly handled: Windows UID/GID skipped, some sticky-bit and symlink timestamp limitations skipped, macOS resource fork only on Darwin.

Test signals: High-value integration coverage for the backup metadata round-trip.
