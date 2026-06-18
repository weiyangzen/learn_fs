# sources/user-network-fs/rclone/cmd/ls/ls.go

Purpose: implements `rclone ls`, the human-readable recursive object listing with size and path.

Important API: Cobra `commandDefinition` registered on `cmd.Root`. It uses shared list help from `cmd/ls/lshelp` and delegates behavior to `operations.List`.

Control flow: requires exactly one `remote:path`, creates a source filesystem via `cmd.NewFsSrc`, then runs `operations.List(context.Background(), fsrc, os.Stdout)` through `cmd.Run(false, false, ...)`.

State/persistence: read-only against the remote and writes only stdout. Dependencies are minimal: root command, list help, and operations. Risks are mainly inherited from filtering/global max-depth behavior and `operations.List` traversal. No direct tests here; behavior is covered through operations/listing tests and command integration.
