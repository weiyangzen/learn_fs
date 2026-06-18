# sources/user-network-fs/s3fs-fuse/test/mknod_test.cc

## Purpose
Helper executable that validates mknod behavior for regular, character, FIFO, socket, and optionally block-special files on the mounted filesystem.

## Important APIs, Types, And Control Flow
`TestMknod` maps a mode to suffix, display name, and device number, creates the node with permissions, stats it, verifies `S_IFMT`, and unlinks it. `main` parses one base path or help, checks length, skips block-device testing unless effective uid is root, and fails if any required node type cannot be created/stat-verified.

## State And Persistence
Creates and removes several filesystem nodes named from the base path with `.reg`, `.chr`, `.fifo`, `.sock`, and optionally `.blk` suffixes. Failed cleanup can leave nodes behind.

## Dependencies And Integration Points
Depends on POSIX `mknod`, `stat`, `unlink`, `geteuid`, and `makedev`; macOS/FreeBSD include handling differs. Called by `integration-test-main.sh` from `test_mknod`.

## Risks And Test Signals
Some node types are unsupported or permission-sensitive on FUSE and host systems. The fixed path length cap is conservative. The integration signal is whether s3fs correctly rejects or represents special node creation according to expected FUSE semantics.
