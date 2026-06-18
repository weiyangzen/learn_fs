# sources/user-network-fs/rclone/cmd/serve/nfs/filesystem.go

## Purpose

`filesystem.go` adapts rclone VFS to the `go-billy` filesystem interfaces consumed by go-nfs.

## Important APIs, Types, and Functions

`FS` stores a VFS pointer and optional rooted subpath. It implements `ReadDir`, `Create`, `Open`, `OpenFile`, `Stat`, `Rename`, `Remove`, `Join`, `TempFile`, `MkdirAll`, `Lstat`, `Symlink`, `Readlink`, `Chmod`, `Lchown`, `Chown`, `Chtimes`, `Chroot`, `Root`, and `Capabilities`. `setSys` attaches go-nfs `file.FileInfo` ownership and inode metadata to VFS nodes.

## Control Flow

Each method rewrites relative names through `fullPath`, traces the operation, then delegates to VFS. Directory and stat paths call `setSys` so NFS sees UID, GID, nlink, and file IDs. `MkdirAll` manually creates missing path prefixes to preserve permissions.

## State and Persistence Behavior

FS state is a view over a shared VFS and optional root. Write methods mutate the served remote through VFS. `setSys` mutates per-node Sys metadata.

## Dependencies and Integration Points

It integrates go-billy, go-nfs file metadata, rclone VFS, VFS cache mode, and subpath mount handling from `handler.go`.

## Risks and Test Signals

Risks include path.Join behavior for absolute/empty paths, partial `MkdirAll` behavior, masking `Chmod` ENOSYS, file close logging format, capability reporting based on cache mode, and subpath escape assumptions. Handler tests exercise subpath reads/writes and root visibility.
