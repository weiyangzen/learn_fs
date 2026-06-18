# sources/sync-backup/kopia/cli/auto_upgrade.go

## Purpose
Repository auto-upgrade helper invoked while opening repositories. It detects unsupported format parameters, attempts a direct write-session upgrade when allowed, and seeds default maintenance parameters after successful upgrades.

## APIs, Types, and Functions
Important APIs include functions/methods `maybeAutoUpgradeRepository`, `setDefaultMaintenanceParameters`.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The implementation opens a write session, requires direct repository writer access, persists maintenance parameters. State and persistence: touches maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/maintenance plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
