# sources/sync-backup/restic/cmd/restic/cmd_tag.go

Purpose: implements `restic tag`, modifying tags on selected snapshots by setting, adding, or removing tags.

Important APIs/types/functions: `TagOptions`; JSON structs `changedSnapshot` and `changedSnapshotsSummary`; `changeTags`; `runTag`.

Control flow and state: validates that some tag action is requested and `--set` is not combined with add/remove, opens exclusive lock, chooses text or JSON print callbacks, iterates filtered snapshots, mutates snapshot tags, preserves original snapshot ID, saves a new snapshot file, removes the old snapshot file, and prints a changed summary. Setting a single empty tag means no tags.

Dependencies and integration points: uses `data.TagLists`, snapshot filtering, repository snapshot save/remove, debug logging, and JSON terminal output.

Risks: command rewrites snapshot metadata by creating new IDs, so consumers must follow `Original`. Errors per snapshot are printed and ignored, allowing partial success. Tag order is determined by `data.Snapshot` helpers.

Test signals: tag integration test covers set, add, remove, remove all, original ID preservation, and repository check after each mutation.
