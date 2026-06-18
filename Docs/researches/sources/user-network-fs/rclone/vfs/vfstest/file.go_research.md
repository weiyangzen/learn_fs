# sources/user-network-fs/rclone/vfs/vfstest/file.go

## Purpose
Tests file modtime behavior and VFS symlink support across direct VFS and mounted operation.

## APIs, Flow, And State
`TestFileModTime` and `TestFileModTimeWithOpenWriters` set mtimes and verify Unix timestamps after close/writeback. `TestSymlinks` creates real files/directories, then exercises file and directory symlinks, read/write through links, rename/delete of links, mode reporting, and conflict cases where regular files, directories, and link metadata names overlap. Several complex move-conflict cases are marked skipped.

## Dependencies And Integration
Depends on the `run` harness, `vfscommon` permission defaults, `fs.LinkSuffix`, and platform symlink semantics. Link tests only run when `run.vfsOpt.Links` is enabled and skip Windows.

## Risks And Test Signals
Risks include losing mtimes when writers close, incorrect link-file translation, link-vs-regular conflict handling, and divergence between direct VFS and OS-resolved mount symlink behavior. The skipped FIXME cases document remaining unimplemented conflict coverage.
