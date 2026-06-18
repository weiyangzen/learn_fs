<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot.go -->
# sources/sync-backup/kopia/cli/command_snapshot.go

## Purpose
Registers the `kopia snapshot`/`snap` command namespace and wires all snapshot-management subcommands into the CLI.

## Important APIs, Types, And Functions
The `commandSnapshot` struct owns `copyHistory`, `moveHistory`, `create`, `delete`, `estimate`, `expire`, `fix`, `list`, `migrate`, `pin`, `restore`, and `verify` command objects.

## Control Flow
`setup` creates the parent command, then calls each child setup method. Copy and move history reuse the same command implementation with different mode flags.

## State And Persistence Behavior
This file has no runtime state beyond child command structs. Persistent snapshot behavior is implemented by the child files.

## Dependencies And Integration Points
Integrates many CLI modules under the `advancedAppServices` capability boundary because some children need advanced repository/password services.

## Risks And Edge Cases
Risks are command registration omissions and alias conflicts. A child setup failure or renamed command can make functionality unreachable even if implementation files compile.

## Test Signals
Test signals are CLI help/parse tests and smoke tests for each subcommand under both `snapshot` and `snap` aliases.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot.go -->
