# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_tree_walker.go

Purpose: parallel, de-duplicating traversal of repository-backed snapshot filesystem trees.

Important APIs/types/functions: `EntryCallback`, `TreeWalker`, `ReportError`, `GetErrors`, `Err`, `TooManyErrors`, `Process`, `Close`, `TreeWalkerOptions`, and `NewTreeWalker`.

Control flow: `Process` rejects entries without object IDs, dedupes by object ID in a `bigmap.Set`, invokes the callback, and recursively processes directories. Directory children may be handled through a workshare pool. Iteration stops early when `MaxErrors` is reached.

State and persistence: in-memory walker state persists across multiple `Process` calls, so the same walker skips objects already seen in previous roots. It records total error count plus a bounded list of errors.

Dependencies and integration points: used by verifier, snapshot GC, and storage stats to avoid reprocessing shared objects.

Risks and test signals: dedupe by object ID means identical content at different paths is visited once. `MaxErrors <= 0` means unlimited but only one stored error when zero. Tests cover dedupe, missing object ID, single/multiple errors, and shared-OID errors.
