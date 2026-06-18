<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/handler.go

Source read: complete file, 194 lines, 4185 bytes, sha256 `a1a11939c64570a9c454b6c3cf568760ade1d1d77d8e0f8e6baba26461dbf9c5`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/handler.go_research.md`.

## Purpose
Maps `pkg/sftp` file operation interfaces onto rclone VFS operations.

## Important APIs, types, and functions
`vfsHandler` embeds VFS and implements `Fileread`, `Filewrite`, `Filecmd`, `StatVFS`, `Filelist`, plus `listerat.ListAt`.

## Control flow
Read/write open VFS files according to SFTP flags. File commands implement Setstat size/mtime, Rename, Remove/Rmdir, Mkdir, and reject symlink/hardlink. Listing stats directories/files and adapts results to SFTP's `ListerAt` interface.

## State and persistence behavior
State mutations are remote file writes, truncates, modtime changes, renames, removals, and mkdirs through VFS. No extra local persistence.

## Dependencies and integration points
Depends on `pkg/sftp`, VFS node/handle APIs, os flags, syscall errors, and VFS statfs.

## Risks and edge cases
Flag handling must preserve resume semantics: absence of truncate must not zero existing content. Symlink/readlink are unsupported. StatVFS invents inode counts because VFS has no inode model.

## Test signals
`handler_test.go` validates resume without truncate, truncation, Setstat size, StatVFS, and mtime setting. Interface assertions in `sftp_test.go` confirm SFTP contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler.go -->
