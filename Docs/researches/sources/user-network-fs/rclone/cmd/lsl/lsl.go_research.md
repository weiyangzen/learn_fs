# sources/user-network-fs/rclone/cmd/lsl/lsl.go

Purpose: implements `rclone lsl`, recursively listing objects with modification time, size, and path.

Important API: Cobra `commandDefinition` and `operations.ListLong`. It appends shared list help and is marked in Filter/Listing groups.

Control flow: validates exactly one source arg, creates source Fs, and runs `operations.ListLong(context.Background(), fsrc, os.Stdout)` through `cmd.Run(false, false, ...)`.

State/persistence: read-only remote traversal, stdout only. Dependencies are command root, shared list help, and operations. Risks are inherited from backend modtime precision and recursive traversal cost. No direct tests in this subset.
