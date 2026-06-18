<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyto/copyto.go -->
# sources/user-network-fs/rclone/cmd/copyto/copyto.go

## Purpose

`copyto.go` implements `rclone copyto`, copying a file or directory to an explicit destination path/name.

## Important APIs, Types, and Functions

The package mirrors copy's logger globals and setup. `commandDefinition.Run` validates two args, resolves source and destination with `cmd.NewFsSrcDstFiles`, configures operation loggers, and chooses `sync.CopyDir` for directory sources or `operations.CopyFile` with distinct source and destination file names for file sources.

## Control Flow

It runs under `cmd.Run(true, true, ...)` with retry and stats. Destination file parsing only applies when the source resolves as a file.

## State and Persistence Behavior

It writes destination files or directory contents and can overwrite existing files if operations deem them different. Optional logger files may be created.

## Dependencies and Integration Points

It integrates with `cmd.NewFsSrcDstFiles`, `operationsflags`, `operations.CopyFile`, and `sync.CopyDir`.

## Risks and Test Signals

Risks include ambiguous missing source paths, destination file/dir inference, logger lifecycle, and retrying partially written explicit filenames. Tests should cover file renames, directory copy behavior, destination existing as file, filters, logger flags, and overwrite/no-op cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyto/copyto.go -->
