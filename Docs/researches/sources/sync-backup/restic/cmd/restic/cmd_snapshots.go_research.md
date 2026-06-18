# sources/sync-backup/restic/cmd/restic/cmd_snapshots.go

Purpose: implements `restic snapshots`, listing snapshots with filtering, grouping, latest limits, text tables, and JSON output.

Important APIs/types/functions: `SnapshotOptions`; `runSnapshots`; `filterLatestSnapshotsInGroup`; `PrintSnapshots`; `PrintSnapshotGroupHeader`; JSON wrapper types `Snapshot` and `SnapshotGroup`; `printSnapshotGroupJSON`.

Control flow and state: opens read lock, streams filtered snapshots, groups them by configured host/path/tag options, optionally keeps latest N per group, sorts lists newest-to-oldest for group storage then text output re-sorts oldest-to-newest. JSON emits either a flat snapshot array or grouped array; text prints optional group headers and tables with summary size when available. No repository mutation occurs.

Dependencies and integration points: uses `FindFilteredSnapshots`, `data.GroupSnapshots`, `data.SnapshotGroupByOptions`, table rendering, UI byte formatting, and global time formatting.

Risks: map iteration makes group order nondeterministic. Text output includes local timezone footer. Deprecated `--last` path remains for compatibility.

Test signals: integration test verifies JSON grouping by host and latest limit; unit test ensures empty JSON is `[]` rather than `null`.
