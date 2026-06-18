# sources/sync-backup/kopia/cli/command_blob_gc.go

## Purpose
Low-level blob garbage-collection command that scans blob storage for unused blobs, supports prefix filtering and parallelism, and only deletes when explicitly requested.

## APIs, Types, and Functions
Important APIs include types `commandBlobGC`; functions/methods `setup`, `run`; Kingpin command(s) gc: Garbage-collect unused blobs; flags delete: Whether to delete unused blobs, parallel: Number of parallel blob scans, prefix: Only GC blobs with given prefix.

## Control Flow, State, and Persistence
Control flow registers command(s) gc: Garbage-collect unused blobs, binds flags delete: Whether to delete unused blobs, parallel: Number of parallel blob scans, prefix: Only GC blobs with given prefix, then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches blob storage objects and metadata, maintenance params, schedule, and maintenance statistics. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/blob, kopia/repo/maintenance plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. parallel scans need cancellation, progress, and error propagation coverage. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
