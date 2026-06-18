# sources/user-network-fs/rclone/cmd/move/move.go

Purpose: implements `rclone move`, moving directory contents or a same-name source file into a destination.

Important APIs/state: flags `--delete-empty-src-dirs`, `--create-empty-src-dirs`, logger flag options, `operationsflags.ConfigureLoggers`, `sync.MoveDir`, and `operations.MoveFile`.

Control flow: validates two args, splits source file vs directory with `cmd.NewFsSrcFileDst`, configures optional transfer loggers, attaches logger to context if requested, then calls `sync.MoveDir` for directory roots or `MoveFile` for a single source file.

State/persistence: mutates source and destination remotes and can delete source data; may write logger outputs depending on flags. Dependencies include sync/operations and logger flags. Risks are data loss, source/destination overlap semantics, global logger option state, and empty-directory flags on backends without real directories. Test signal is likely in sync/operations integration suites.
