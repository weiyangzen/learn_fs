# File Research: sources/virtualization/qemu/block/qcow2-snapshot.c

Implements qcow2 internal snapshot table parsing, writing, validation/repair, snapshot creation, rollback, deletion, listing, and temporary read-only snapshot loading.

Key entry points:
- `qcow2_read_snapshots()` loads the snapshot table through `qcow2_do_read_snapshots()` in strict mode.
- `qcow2_write_snapshots()` writes a complete replacement snapshot table, updates the qcow2 header pointer/count only after flushing the new table, then frees the old table.
- `qcow2_check_read_snapshot_table()` re-reads snapshot metadata during check mode, optionally truncates excessive snapshot counts/table entries, and records repairable corruption.
- `qcow2_check_fix_snapshot_table()` rewrites the snapshot table when check mode found fixable snapshot-entry corruption.
- `qcow2_snapshot_create()` copies the active L1 table into a new snapshot L1 table, increments referenced-cluster refcounts, appends the snapshot record, writes the table, and discards obsolete VM-state clusters from the active image.
- `qcow2_snapshot_goto()` validates and loads a snapshot L1 table into the active L1 table, resizing the virtual disk if needed and carefully ordering refcount increments before overwriting the current L1 table.
- `qcow2_snapshot_delete()` removes one snapshot record, rewrites the table, then drops the deleted snapshot’s L1/data references.
- `qcow2_snapshot_list()` exports `QEMUSnapshotInfo` records.
- `qcow2_snapshot_load_tmp()` switches a read-only image to a snapshot L1 table without mutating on-disk state.

Core mechanics:
- Snapshot entries include fixed `QCowSnapshotHeader`, known `QCowSnapshotExtraData`, unknown extra data preservation, ID string, and name string, each 8-byte aligned in the table.
- Repair mode can reduce overlarge snapshot counts/tables and truncate excessive extra metadata; it intentionally leaks discarded clusters for `qcow2_check_refcounts()` to recover.
- v3 images require snapshot extra data covering large VM-state size and disk size; incomplete entries are reported and may be rewritten.
- Snapshot lookup supports exact ID/name matching, ID-only, name-only, and ID-or-name rollback lookup.
- All mutating snapshot operations reject images with external data files via `has_data_file(bs)`.

Important invariants:
- Header snapshot pointer/count are updated only after the replacement table and its refcounts are stable.
- New snapshot creation increments data/L2 references before publishing the new snapshot record.
- Snapshot rollback increments the target snapshot references before overwriting the active L1 table, then decrements old active references after the on-disk active L1 has changed.
- Deletion removes the snapshot from the table before freeing its clusters; later failures are tolerated as leaks rather than resurrecting stale table entries.
- Snapshot L1 tables are validated with `qcow2_validate_table()` before use.

Filesystem/block relevance:
- This file implements qcow2’s user-visible internal snapshot lifecycle. It coordinates snapshot metadata with the refcount engine so copy-on-write sharing remains consistent across active and inactive L1/L2 trees.

Notable risks:
- Snapshot repair deliberately trades corruption avoidance for possible leaks, relying on later refcount checking.
- Failure after deleting a snapshot from the table but before freeing its clusters can leak the deleted snapshot’s storage.
- Rollback has delicate ordering because in-memory and on-disk active L1 tables briefly refer to different generations.
