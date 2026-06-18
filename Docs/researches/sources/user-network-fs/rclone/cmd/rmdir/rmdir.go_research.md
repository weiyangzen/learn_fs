# sources/user-network-fs/rclone/cmd/rmdir/rmdir.go

Purpose: implements `rclone rmdir`, removing an empty directory/path.

Important API: Cobra command; uses `cmd.NewFsDir` and `operations.Rmdir`.

Control flow: validates one remote path, creates directory Fs, then runs `operations.Rmdir(context.Background(), fdst, "")` through `cmd.Run(true, false, ...)`.

State/persistence: mutates remote directory/container state only if the target is empty and backend supports removal. Dependencies are operations and command parsing. Risks include backend differences for virtual directories and errors on non-empty paths. Test signal is in operations/backend suites.
