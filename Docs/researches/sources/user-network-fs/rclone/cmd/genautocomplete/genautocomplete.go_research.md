<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete.go

## Purpose

`genautocomplete.go` defines the parent `rclone completion` command and legacy `genautocomplete` alias.

## Important APIs, Types, and Functions

`init` registers `completionDefinition` on `cmd.Root`. The Cobra command contains metadata, help text, annotations, and alias but no `Run`; shell-specific subcommands provide behavior.

## Control Flow

Invoking the parent without a shell relies on Cobra help behavior. Subcommand registration happens from sibling files' init functions.

## State and Persistence Behavior

The parent command itself creates no files and mutates no state beyond command registration.

## Dependencies and Integration Points

It integrates Cobra with bash, fish, powershell, and zsh completion subcommands.

## Risks and Test Signals

Risks are alias compatibility and missing subcommand registration due to build/package changes. Tests should verify parent help, alias availability, and shell subcommands attached.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete.go -->
