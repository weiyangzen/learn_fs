# sources/storage-engines/tikv/components/engine_traits/src/snapshot_misc.rs

Purpose: Declares miscellaneous snapshot extension behavior.

Important APIs and control flow: `SnapshotMiscExt` exposes `sequence_number`, returning the backend sequence number for the snapshot.

State, persistence, and dependencies: The sequence number represents a snapshot's persisted/logical read point; this trait stores nothing itself.

Integration points, risks, and test signals: Used by read consistency, cache engine coordination, and recovery diagnostics. Risks include backends without meaningful sequence numbers, sequence mismatch with region cache snapshots, and stale values after compaction. Tests are implementor-specific.
