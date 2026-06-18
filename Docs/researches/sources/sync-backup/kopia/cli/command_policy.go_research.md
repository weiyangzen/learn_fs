# sources/sync-backup/kopia/cli/command_policy.go

## Purpose
Command group root and target flag parsing for snapshot policy commands. It selects global, host/user/path, or explicit policy targets for sibling policy operations.

## APIs, Types, and Functions
Important APIs include types `commandPolicy`, `policyTargetFlags`; functions/methods `setup`, `setup`, `policyTargets`; Kingpin command(s) policy: Commands to manipulate snapshotting policies.; flags global: Select the global policy.; arguments target: Select a particular policy (a per-host policy `@host`, a per-user policy `user@host`, a per-path policy `user@host:path` or a local path). Use --global to target the global policy..

## Control Flow, State, and Persistence
Control flow registers command(s) policy: Commands to manipulate snapshotting policies., binds flags global: Select the global policy., accepts arguments target: Select a particular policy (a per-host policy `@host`, a per-user policy `user@host`, a per-path policy `user@host:path` or a local path). Use --global to target the global policy., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches snapshot policy manifests. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/manifest, github.com/kopia/kopia/snapshot, github.com/kopia/kopia/snapshot/policy. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/manifest, kopia/snapshot, kopia/snapshot/policy plus external packages context, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
