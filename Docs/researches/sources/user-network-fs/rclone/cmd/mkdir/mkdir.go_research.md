# sources/user-network-fs/rclone/cmd/mkdir/mkdir.go

Purpose: implements `rclone mkdir`, creating the destination path if possible.

Important API: Cobra `commandDefinition`; uses `cmd.NewFsDir` and `operations.Mkdir`. It logs a warning when the target backend cannot have empty directories and the root contains a slash, because the operation may be a no-op.

Control flow: validates exactly one remote path, builds a directory Fs, warns on empty-directory-incapable backends, then runs `operations.Mkdir(ctx, fdst, "")` through `cmd.Run(true, false, ...)`.

State/persistence: mutates remote directory/container state when supported. Dependencies are `cmd`, `fs`, `operations`, strings, Cobra. Risks include user confusion on bucket/object stores that cannot represent empty directories. Test signals are probably in operations/backend tests.
