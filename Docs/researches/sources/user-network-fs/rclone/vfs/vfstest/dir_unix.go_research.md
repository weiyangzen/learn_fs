# sources/user-network-fs/rclone/vfs/vfstest/dir_unix.go

## Purpose
Tests that rewinding a mounted directory stream returns the same entries after `lseek(fd, 0, SEEK_SET)`.

## APIs, Flow, And State
`countDirFd` reads raw directory entries from a file descriptor with `syscall.ReadDirent` and parses names. `TestDirRewind` creates a directory with three files, reads once, seeks back to zero, reads again, and compares counts.

## Dependencies And Integration
Unix build-tagged file for Linux, Darwin, and FreeBSD. Exercises the mounted kernel/FUSE path rather than direct VFS and references a regression around go-fuse directory rewind support.

## Risks And Test Signals
The test detects backends that return empty listings after rewind. It is sensitive to platform syscall semantics and skipped for direct VFS mode or missing FUSE.
