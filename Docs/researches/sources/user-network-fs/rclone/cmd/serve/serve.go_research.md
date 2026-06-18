<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/serve.go -->
# sources/user-network-fs/rclone/cmd/serve/serve.go

Source read: complete file, 44 lines, 1137 bytes, sha256 `043ef0aa39cd687790343b2ae7fcb7030513c343567af79e3eaeac08fbed85ee`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/serve.go_research.md`.

## Purpose
Defines the top-level `rclone serve` command under which protocol subcommands register.

## Important APIs, types, and functions
`Command` is a Cobra command with help text and a `RunE` that errors when no protocol or an unknown protocol is supplied. `init` adds it to the root command.

## Control flow
The top-level command itself does not serve traffic; protocol packages call `serve.Command.AddCommand` in their init functions.

## State and persistence behavior
No runtime server state. It only contributes CLI registration and help text.

## Dependencies and integration points
Depends on rclone `cmd` root registration and Cobra.

## Risks and edge cases
Help text mentions metadata headers and delegates actual option behavior to subcommands. Unknown protocols produce a generic error.

## Test signals
Covered indirectly by CLI command registration; protocol tests exercise subcommands.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/serve.go -->
