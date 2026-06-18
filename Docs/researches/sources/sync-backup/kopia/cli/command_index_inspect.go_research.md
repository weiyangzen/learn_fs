# sources/sync-backup/kopia/cli/command_index_inspect.go

## Purpose
Index inspection command that reads index blobs and prints contained content entries, filtering to requested index blob IDs when supplied.

## APIs, Types, and Functions
Important APIs include types `commandIndexInspect`, `indexBlobPlusContentInfo`; functions/methods `setup`, `run`, `runWithOutput`, `inspectAllBlobs`, `dumpIndexBlobEntries`, `shouldInclude`, `inspectSingleIndexBlob`; Kingpin command(s) inspect: Inspect index blob; flags all: Inspect all index blobs in the repository, including inactive, active: Inspect all active index blobs, content-id: Inspect all active index blobs, parallel: Parallelism; arguments blobs: Names of index blobs to inspect.

## Control Flow, State, and Persistence
Control flow registers command(s) inspect: Inspect index blob, binds flags all: Inspect all index blobs in the repository, including inactive, active: Inspect all active index blobs, content-id: Inspect all active index blobs, parallel: Parallelism, accepts arguments blobs: Names of index blobs to inspect, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, slices, sync, github.com/pkg/errors, golang.org/x/sync/errgroup, github.com/kopia/kopia/internal/gather, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/repo/content, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/internal/gather, kopia/repo, kopia/repo/blob, kopia/repo/content, kopia/repo/content/indexblob plus external packages context, slices, sync, github.com/pkg/errors, golang.org/x/sync/errgroup.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. nearby test file `sources/sync-backup/kopia/cli/command_index_inspect_test.go` provides direct coverage.
