<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_fish.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_fish.go

## Purpose

`genautocomplete_fish.go` implements `rclone completion fish`.

## Important APIs, Types, and Functions

`init` attaches `fishCommandDefinition`. The command defaults output to `/etc/fish/completions/rclone.fish`, writes stdout for `-` with `cmd.Root.GenFishCompletion(os.Stdout, true)`, or writes a file through `GenFishCompletionFile`.

## Control Flow

Zero or one argument is accepted. Errors are converted to fatal command failures.

## State and Persistence Behavior

It writes a fish completion script to a local file or stdout.

## Dependencies and Integration Points

It integrates with Cobra fish completion generation and the root command tree.

## Risks and Test Signals

Risks include privileged default path, completion generator API changes, and stale command metadata. Tests should assert custom path and stdout generation produce non-empty fish script output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_fish.go -->
