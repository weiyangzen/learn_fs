# sources/sync-backup/kopia/cli/command_blob_stats.go

## Purpose
Low-level blob statistics command that counts and sizes blobs grouped by prefix or raw numbers, with optional prefix filtering.

## APIs, Types, and Functions
Important APIs include types `commandBlobStats`; functions/methods `setup`, `run`; Kingpin command(s) stats: Blob statistics; flags raw: Raw numbers, prefix: Blob name prefix.

## Control Flow, State, and Persistence
Control flow registers command(s) stats: Blob statistics, binds flags raw: Raw numbers, prefix: Blob name prefix, then runs through a direct repository read action. The implementation iterates blob storage. State and persistence: touches blob storage objects and metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strconv, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/blob plus external packages context, strconv, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
