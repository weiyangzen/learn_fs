# sources/sync-backup/kopia/cli/command_index_recover.go

## Purpose
Dangerous index recovery command that reconstructs index entries from pack blobs, optionally deleting old indexes and committing recovered metadata only with explicit flags.

## APIs, Types, and Functions
Important APIs include types `commandIndexRecover`; functions/methods `setup`, `run`, `recoverIndexesFromAllPacks`, `recoverIndexFromSinglePackFile`; Kingpin command(s) recover: Recover indexes from pack blobs; flags blob-prefixes: Prefixes of pack blobs to recover from (default=all packs), blobs: Names of pack blobs to recover from (default=all packs), parallel: Recover parallelism, ignore-errors: Ignore errors when recovering, delete-indexes: Delete all indexes before recovering, commit: Commit recovered content.

## Control Flow, State, and Persistence
Control flow registers command(s) recover: Recover indexes from pack blobs, binds flags blob-prefixes: Prefixes of pack blobs to recover from (default=all packs), blobs: Names of pack blobs to recover from (default=all packs), parallel: Recover parallelism, ignore-errors: Ignore errors when recovering, delete-indexes: Delete all indexes before recovering, commit: Commit recovered content, then runs through a direct repository write action. The implementation iterates blob storage, deletes blob storage objects, reconstructs index entries from pack blobs. State and persistence: touches blob storage objects and metadata, content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sync/atomic, time, github.com/pkg/errors, golang.org/x/sync/errgroup, github.com/kopia/kopia/internal/timetrack, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/internal/timetrack, kopia/repo, kopia/repo/blob, kopia/repo/content, kopia/repo/content/indexblob plus external packages context, sync/atomic, time, github.com/pkg/errors, golang.org/x/sync/errgroup.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
