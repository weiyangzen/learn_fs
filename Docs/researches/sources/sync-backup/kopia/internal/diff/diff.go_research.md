# sources/sync-backup/kopia/internal/diff/diff.go

Purpose: compares two Kopia filesystem trees, emits human-readable differences, accumulates stats, optionally runs an external diff command, and finds related snapshot manifests.

Important APIs/types/functions: `EntryTypeStats`, `Stats`, `Comparer`, `Compare`, `Close`, `Stats`, `NewComparer`, `GetPrecedingSnapshot`, `GetTwoLatestSnapshotsForASource`, `compareEntry`, `compareDirectories`, `compareFiles`, and `compareMetadata`.

Control flow: comparison recurses directory entries by name. Matching object IDs short-circuit content comparison but still check metadata. Adds/removes update stats and can download files to temp `old/` and `new/` paths for external diff. Existing entries compare metadata, type changes, and file changes. Snapshot helpers sort manifests by start time and return predecessor/latest pair.

State and persistence behavior: comparer owns a temp directory removed by `Close`; external diff downloads transient file copies. Stats are reset per `Compare`.

Dependencies/integration: integrates `fs`, `object`, `snapshotfs`, `snapshot`, `repo`, external commands, and `iocopy`.

Risks/test signals: external diff exit status is ignored. Directory comparison assumes names are unique. Tests cover directory/file changes, metadata-only object-ID matches, stats, and snapshot helper ordering/errors.
