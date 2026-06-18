<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir.go -->
# sources/user-network-fs/rclone/fs/dir.go

## Purpose
Provides `Dir`, a generic implementation of rclone's `Directory`/`DirEntry` interfaces for unspecialized directories, buckets, or containers.

## Important APIs, Types, And Control Flow
Constructors `NewDir` and `NewDirCopy` initialize remote path, modtime, size/items defaults, filesystem info, and optional IDs. Methods expose and fluently mutate remote, ID, parent ID, size, and items. `ModTime` returns stored time or configured default directory time when unknown.

## State And Persistence
Each `Dir` is an in-memory value. It references `fs.ConfigInfo.DefaultTime` when modtime is zero.

## Dependencies And Integration Points
Implements `DirEntry` and `Directory`; used by list results, dirtree synthesis, and backends that need simple directory objects.

## Risks And Test Signals
`NewDirCopy` copies ID but not parent ID. Unknown modtimes depend on context config. Interface compile checks are present; behavior is tested indirectly by dirtree and directory entry tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir.go -->
