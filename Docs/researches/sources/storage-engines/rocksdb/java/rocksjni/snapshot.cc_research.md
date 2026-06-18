<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/snapshot.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/snapshot.cc

Purpose: Exposes `Snapshot::GetSequenceNumber` to Java.

Important APIs/types/functions: `Java_org_rocksdb_Snapshot_getSequenceNumber` reinterprets a snapshot handle and returns `snapshot->GetSequenceNumber()`.

Control flow: Java obtains a snapshot handle from `RocksDB.getSnapshot`, then this method reads its sequence number. Release is handled in `rocksjni.cc`, not here.

State and persistence behavior: Snapshot state is owned by the DB. This file only reads the sequence number and does not mutate persistence.

Dependencies and integration points: Includes generated `org_rocksdb_Snapshot.h`, `rocksdb/db.h`, and `portal.h`. Integrates with the DB snapshot lifecycle in `rocksjni.cc`.

Risks: No null/stale handle checks. Using this after `ReleaseSnapshot` or DB close is unsafe.

Test signals: Tests should assert sequence numbers are stable for a snapshot and increase across writes/new snapshots, and that Java wrappers prevent use after release.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/snapshot.cc -->
