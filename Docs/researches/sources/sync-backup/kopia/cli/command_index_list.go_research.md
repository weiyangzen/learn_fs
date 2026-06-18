# sources/sync-backup/kopia/cli/command_index_list.go

## Purpose
Index listing command that enumerates active and optionally superseded index blobs, with summary and sort modes by time, size, or name.

## APIs, Types, and Functions
Important APIs include types `commandIndexList`; functions/methods `setup`, `run`; Kingpin command(s) list: List content indexes; flags summary: Display index blob summary, superseded: Include inactive index files superseded by compaction, sort: Index blob sort order.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List content indexes, binds flags summary: Display index blob summary, superseded: Include inactive index files superseded by compaction, sort: Index blob sort order, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches content index blobs and epoch metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/pkg/errors, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/repo plus external packages context, sort, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
