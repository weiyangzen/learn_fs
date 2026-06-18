## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/filter/ReclaimableRenameEntryFilter.java

Purpose: reclaim filter for rename-table entries, deleting them only when the previous snapshot no longer references the renamed object.

Important APIs and types: extends `ReclaimableFilter<String>` with one previous snapshot. Overrides volume/bucket parsing via `metadataManager.splitRenameKey`, and `isReclaimable` checks previous key and directory tables.

Control flow: for each rename entry, opens previous snapshot tables if available. It looks up the rename entry value as the previous DB key in key and, for FSO buckets, directory tables. If any table contains an object with that DB key, the rename entry is retained; otherwise it is reclaimable.

State and persistence: no durable writes; uses base class cached previous snapshot handles and locks.

Dependencies and integration: used by snapshot GC of rename tables. Depends on rename key encoding, bucket layout, and `WithObjectID` table values.

Risks and test signals: if rename value encoding does not match previous table DB key format, entries may be reclaimed too early. Tests should cover OBS key-only lookup, FSO key plus directory lookup, no previous snapshot, splitRenameKey parsing, null previous tables, and chain-change validation inherited from `ReclaimableFilter`.
