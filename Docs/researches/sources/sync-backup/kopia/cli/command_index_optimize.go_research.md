# sources/sync-backup/kopia/cli/command_index_optimize.go

## Purpose
Index optimization command that runs index compaction with thresholds for small blobs, deleted-content age, all-index forcing, and explicit content dropping.

## APIs, Types, and Functions
Important APIs include types `commandIndexOptimize`; functions/methods `setup`, `runOptimizeCommand`; Kingpin command(s) optimize: Optimize indexes blobs.; flags max-small-blobs: Maximum number of small index blobs that can be left after compaction., drop-deleted-older-than: Drop deleted contents above given age, drop-contents: Drop contents with given IDs, all: Optimize all indexes, even those above maximum size..

## Control Flow, State, and Persistence
Control flow registers command(s) optimize: Optimize indexes blobs., binds flags max-small-blobs: Maximum number of small index blobs that can be left after compaction., drop-deleted-older-than: Drop deleted contents above given age, drop-contents: Drop contents with given IDs, all: Optimize all indexes, even those above maximum size., then runs through a direct repository write action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/content/indexblob. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/content/indexblob plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
