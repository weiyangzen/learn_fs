# sources/sync-backup/kopia/cli/command_cache.go

## Purpose
Command group root for local cache operations. It wires cache clear/info/prefetch/set/sync subcommands into the CLI.

## APIs, Types, and Functions
Important APIs include types `commandCache`; functions/methods `setup`; Kingpin command(s) cache: Commands to manipulate local cache.

## Control Flow, State, and Persistence
Control flow registers command(s) cache: Commands to manipulate local cache, then runs through a test/helper flow. The implementation persists maintenance parameters. State and persistence: touches local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
