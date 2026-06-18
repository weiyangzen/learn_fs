# sources/sync-backup/kopia/cli/command_maintenance_run.go

## Purpose
Maintenance run command that triggers quick or full repository maintenance, with safety flags and optional force override for owner checks.

## APIs, Types, and Functions
Important APIs include types `commandMaintenanceRun`; functions/methods `setup`, `run`; Kingpin command(s) run: Run repository maintenance; flags full: Full maintenance, force: Run maintenance even if not owned (unsafe).

## Control Flow, State, and Persistence
Control flow registers command(s) run: Run repository maintenance, binds flags full: Full maintenance, force: Run maintenance even if not owned (unsafe), then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance, github.com/kopia/kopia/snapshot/snapshotmaintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/maintenance, kopia/snapshot/snapshotmaintenance plus external packages context.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
