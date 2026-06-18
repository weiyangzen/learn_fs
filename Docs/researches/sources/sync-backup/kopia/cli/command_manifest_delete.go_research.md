# sources/sync-backup/kopia/cli/command_manifest_delete.go

## Purpose
Raw manifest deletion command that removes manifests by ID from repository metadata.

## APIs, Types, and Functions
Important APIs include types `commandManifestDelete`; functions/methods `setup`, `run`; Kingpin command(s) delete: Remove manifest items; arguments item: Items to remove.

## Control Flow, State, and Persistence
Control flow registers command(s) delete: Remove manifest items, accepts arguments item: Items to remove, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches repository manifest metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
