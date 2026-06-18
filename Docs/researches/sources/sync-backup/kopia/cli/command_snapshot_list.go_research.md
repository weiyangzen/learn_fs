<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list.go -->
# sources/sync-backup/kopia/cli/command_snapshot_list.go

## Purpose
Implements `snapshot list`/`ls`, including source/path matching, tag filtering, JSON output, human-readable rows, identical snapshot compaction, retention/pin display, delta display, and optional storage-stat calculation.

## Important APIs, Types, And Functions
Key symbols include `commandSnapshotList`, `findSnapshotsForSource`, `findRelativePathParts`, `findManifestIDs`, `SnapshotManifest`, `outputJSON`, `outputManifestGroups`, `outputManifestFromSingleSource`, `mergeIdenticalRows`, `outputSnapshotRows`, `entryBits`, and `deltaBytes`.

## Control Flow
The command parses tag filters, finds matching manifest IDs for all sources or a requested source/path and its parents, loads manifests, then either emits JSON groups or text groups. Text mode filters to current user/host unless `--all`, computes retention reasons, resolves nested entries from snapshot roots, optionally computes storage stats, builds rows, compacts identical object IDs, and prints formatted bits.

## State And Persistence Behavior
It is read-only unless storage-stat calculation mutates in-memory `StorageStats` fields on manifests. It observes snapshot manifests, policy retention reasons, snapshot root objects, directory summaries, pins, and object IDs.

## Dependencies And Integration Points
Integrates snapshot manifest APIs, policy retention logic, snapshotfs root/nested-entry helpers, storage-stat calculation, object IDs, color output, and shared JSON/timestamp/unit helpers.

## Risks And Edge Cases
Risks include parent-path search returning more manifests than users expect, `--max-results` slicing after sort direction, identical compaction hiding metadata differences, and delta comparing entry size to previous manifest total file size. Loading nested paths can emit per-row errors rather than failing the command.

## Test Signals
Tests should cover JSON, tags, source filtering, `--all`, nested paths, incomplete snapshots, retention/pins, identical compaction, reverse/max-results, and storage-stat output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_list.go -->
