# sources/storage-engines/rocksdb/db/snapshot_impl.h

## Purpose

`snapshot_impl.h` defines RocksDB's internal snapshot records and snapshot containers. `SnapshotImpl` extends the public `Snapshot` interface with sequence number, Unix time, timestamp, write-conflict-boundary state, and doubly-linked-list membership. `SnapshotList` manages ordinary snapshots, while `TimestampedSnapshotList` manages timestamp-keyed shared snapshots.

## Important APIs, Types, and Functions

`SnapshotImpl` exposes `GetSequenceNumber`, `GetUnixTime`, and `GetTimestamp`. `SnapshotList::New` inserts a caller-owned `SnapshotImpl` at the newest end of a circular list. `Delete` unlinks without freeing. `GetAll` returns sorted, deduplicated snapshot sequence numbers up to `max_seq` and can return the oldest write-conflict-boundary snapshot. `GetNewest`, `GetOldestSnapshotTime`, `GetOldestSnapshotSequence`, and `count` expose list metadata. `TimestampedSnapshotList` provides `GetSnapshot`, range lookup through `GetSnapshots`, `AddSnapshot`, and `ReleaseSnapshotsOlderThan`.

## Control Flow

Ordinary snapshots are appended to the circular list in creation order and removed by pointer. `GetAll` walks oldest to newest, stops once sequence exceeds `max_seq`, deduplicates repeated sequence numbers, and records the first write-conflict boundary. Timestamped snapshots use `std::map<uint64_t, shared_ptr<const SnapshotImpl>>`; lookup with max timestamp returns the latest snapshot, while release moves old shared pointers into a caller-provided container before erasing map entries.

## State and Persistence Behavior

Snapshot state is in-memory only, but it pins sequence ranges that affect compaction, history trimming, and transaction conflict checking. `SnapshotList` uses a dummy head node initialized with debug placeholder fields. `TimestampedSnapshotList` requires DB mutex protection and keeps shared ownership so erased timestamp entries can be released outside helper code while preserving lifetime.

## Dependencies and Integration Points

The header depends on `dbformat`, public `DB`/`Snapshot`, `autovector`, and STL containers. `DBImpl`, transaction code, compaction, and timestamped snapshot APIs use these lists to collect active snapshots and retention boundaries.

## Risks and Test Signals

Risks include list corruption from unprotected concurrent access, forgetting that `Delete` does not free, duplicate timestamp insertions being ignored by `try_emplace`, and releasing timestamped snapshots without DB mutex coordination. Tests should cover insertion/removal order, duplicate sequence deduplication, max-sequence filtering, write-conflict boundary discovery, timestamp range queries, latest-timestamp lookup, and release-before-threshold behavior.
