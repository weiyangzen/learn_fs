# sources/user-network-fs/rclone/cmd/moveto/moveto.go

Purpose: implements `rclone moveto`, moving or renaming a file to a specific destination path, or moving a directory to a target directory.

Important APIs/state: logger flag globals; `cmd.NewFsSrcDstFiles`; `operations.MoveFile`; `sync.MoveDir`.

Control flow: validates two args, splits source/destination filesystem and file names. After optional logger configuration, directory sources call `sync.MoveDir(ctx, fdst, fsrc, false, false)` while file sources call `operations.MoveFile(ctx, fdst, fsrc, dstFileName, srcFileName)`.

State/persistence: mutates source/destination remotes and deletes source on success. Dependencies are command parsing, operations logging, sync/move. Risks include data loss/overwrite, directory mode using fixed false empty-dir flags, and logger global state. Tests are indirect in operations/sync command coverage.
