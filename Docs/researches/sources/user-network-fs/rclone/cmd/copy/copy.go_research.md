<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copy/copy.go -->
# sources/user-network-fs/rclone/cmd/copy/copy.go

## Purpose

`copy.go` implements `rclone copy`, copying source contents to a destination without deleting extra destination files.

## Important APIs, Types, and Functions

Globals hold `createEmptySrcDirs`, `loggerOpt`, and `loggerFlagsOpt`. `init` registers the command, the empty-dir flag, and operation logger flags. The Cobra `Run` resolves source/file/destination via `cmd.NewFsSrcFileDst`, configures optional loggers, injects the sync logger into context, and calls `sync.CopyDir` for directory sources or `operations.CopyFile` for single-file sources.

## Control Flow

The command runs with retries and stats. Logger setup happens inside the retry closure, so each attempt owns its logger cleanup.

## State and Persistence Behavior

It writes or updates destination objects and optionally creates empty source directories at the destination. It can create local logger output files depending on logger flags.

## Dependencies and Integration Points

It integrates with `operationsflags`, `operations.CopyFile`, `sync.CopyDir`, Fs helper parsing, filters, and global transfer accounting.

## Risks and Test Signals

Risks include source file detection edge cases, repeated logger setup on retries, empty-directory semantics, metadata/root-directory expectations, and retrying partial copies. Tests should cover file vs directory copy, logger flag outputs, empty dirs, filters, no-traverse behavior through sync, and error/retry propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copy/copy.go -->
