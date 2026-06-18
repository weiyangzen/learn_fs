# sources/sync-backup/kopia/cli/command_index_epoch_list.go

## Purpose
Index epoch listing command that reads epoch manager state and reports epoch IDs, ranges, compaction state, or related index metadata.

## APIs, Types, and Functions
Important APIs include types `commandIndexEpochList`; functions/methods `setup`, `run`; Kingpin command(s) list: List the status of epochs..

## Control Flow, State, and Persistence
Control flow registers command(s) list: List the status of epochs., then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content indexes, pack blobs, and content metadata, content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/blob. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/blob plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
