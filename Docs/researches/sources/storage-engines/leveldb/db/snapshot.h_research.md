# sources/storage-engines/leveldb/db/snapshot.h

Purpose: implements DB snapshot bookkeeping as a circular doubly linked list of immutable sequence-number handles. Snapshots let reads and iterators observe a stable sequence boundary while newer writes continue.

Important APIs and types: `SnapshotImpl`, `SnapshotList`, `SnapshotImpl::sequence_number`, `SnapshotList::empty`, `oldest`, `newest`, `New`, and `Delete`.

Control flow: `SnapshotList` uses a dummy `head_` node. `New` asserts monotonically nondecreasing sequence numbers, allocates a `SnapshotImpl`, and appends it at the tail. `Delete` unlinks the snapshot from its current neighbors and deletes it.

State and persistence behavior: snapshots are in-memory only and are not persisted across DB reopen. The oldest snapshot is used by DB internals to retain obsolete versions/files and sequence-visible memtable entries.

Dependencies and integration: derives from public `leveldb::Snapshot` and uses `SequenceNumber` from `dbformat.h`. `DBImpl::GetSnapshot` and `ReleaseSnapshot` own the synchronization around this list.

Risks and edge cases: `Delete` takes a const pointer to match public API but deallocates it. Debug builds track `list_` to assert release through the correct list; release through the wrong DB is a user error. Callers must hold the DB mutex when mutating the list.

Test signals: snapshot behavior is indirectly tested by DB iterator/read tests and issue regressions such as snapshot-heavy issue 320.
