# sources/object-store/minio-mc/cmd/retention-main.go

## Purpose
Defines the top-level `mc retention` command and wires its subcommands.

## Important APIs, types, and functions
- `retentionSubcommands` contains `retentionSetCmd`, `retentionClearCmd`, and `retentionInfoCmd`.
- `retentionCmd` registers command name, usage, global flags, and `setGlobalsFromContext`.
- `mainRetention` delegates unknown or missing subcommands to `commandNotFound`.

## Control flow
The top-level action does not execute retention logic. Actual behavior lives in the selected subcommand. If invoked without a valid subcommand, it reports command-not-found/help through the shared command dispatcher.

## State and persistence
No state. This file only registers command metadata.

## Dependencies and integration points
Integrates with the MinIO CLI command tree and the subcommands implemented in `retention-set.go`, `retention-clear.go`, and `retention-info.go`.

## Risks and edge cases
Minimal. The main risk is command tree drift if a subcommand is renamed but not updated in `retentionSubcommands`.

## Test signals
No direct tests. CLI command registration tests could assert the three subcommands are present and global setup is attached.
