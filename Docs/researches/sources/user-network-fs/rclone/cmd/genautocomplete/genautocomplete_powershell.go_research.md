<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_powershell.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_powershell.go

## Purpose

`genautocomplete_powershell.go` implements `rclone completion powershell`.

## Important APIs, Types, and Functions

`init` attaches `powershellCommandDefinition`. The command writes to stdout when no output file is supplied or the arg is `-`, using `cmd.Root.GenPowerShellCompletion`; otherwise it writes a file with `GenPowerShellCompletionFile`.

## Control Flow

The default path is stdout, unlike bash/fish/zsh. Argument validation allows zero or one arg; errors are fatal.

## State and Persistence Behavior

It writes completion script text to stdout or a chosen local file.

## Dependencies and Integration Points

It depends on Cobra PowerShell generation and rclone command registration.

## Risks and Test Signals

Risks include profile-loading assumptions, stdout capture in tests, and unsupported shell syntax after Cobra changes. Tests should cover missing arg, `-`, custom file, and non-empty generated script.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_powershell.go -->
