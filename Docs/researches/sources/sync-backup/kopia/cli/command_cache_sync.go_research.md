# sources/sync-backup/kopia/cli/command_cache_sync.go

## Purpose
Cache synchronization command that flushes cached content/index/blob-list state to durable storage for the connected repository.

## APIs, Types, and Functions
Important APIs include types `commandCacheSync`; functions/methods `setup`, `run`; Kingpin command(s) sync: Synchronizes the metadata cache with blobs in storage; flags parallel: Fetch parallelism.

## Control Flow, State, and Persistence
Control flow registers command(s) sync: Synchronizes the metadata cache with blobs in storage, binds flags parallel: Fetch parallelism, then runs through a direct repository write action. The implementation iterates blob storage. State and persistence: touches content indexes, pack blobs, and content metadata, local cache directories and client cache parameters. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, golang.org/x/sync/errgroup, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob, kopia/repo/content plus external packages context, github.com/pkg/errors, golang.org/x/sync/errgroup.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. nearby test file `sources/sync-backup/kopia/cli/command_cache_sync_test.go` provides direct coverage.
