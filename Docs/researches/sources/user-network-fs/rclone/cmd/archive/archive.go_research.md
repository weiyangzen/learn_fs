# sources/user-network-fs/rclone/cmd/archive/archive.go

Purpose: non-Plan 9 root command for `rclone archive`. It registers `archive.Command` and provides help text directing users to subcommands such as `list`, `create`, and `extract`.

Control flow: `init` adds the command to `cmd.Root`; `RunE` returns an explicit error when no action is provided or an unknown action is used, leaving real work to subcommands. State is command registration only. Dependencies are Cobra and rclone command root. Risks are mostly UX: root command does no subcommand dispatch beyond Cobra and returns generic unknown action. Test signal is indirect through archive command tests and command docs.
