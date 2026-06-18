# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker_test.go

Purpose: exercises `TreeWalker` traversal, dedupe, and error reporting.

Important APIs/types/functions: `TestSnapshotTreeWalker`, `TestSnapshotTreeWalker_Errors`, `TestSnapshotTreeWalker_MultipleErrors`, and `TestSnapshotTreeWalker_MultipleErrorsSameOID`.

Control flow: tests first assert processing a local mock directory without object IDs fails. They upload mock trees, process snapshot roots, count callback invocations, reprocess roots to verify dedupe, add new content to verify only new objects are visited, and inject callback errors by entry path.

State and persistence: uses a test repository populated through `upload.NewUploader`; walker state persists within each test until `Close`.

Dependencies and integration points: covers uploader output, `SnapshotRoot`, repository-backed filesystem entries, and workshare-disabled deterministic paths with `Parallelism: 1`.

Risks and test signals: shared object IDs deliberately collapse multiple paths into one callback/error opportunity. Expected callback counts encode object sharing assumptions for directories and files.
