# sources/storage-engines/leveldb/include/leveldb/db.h

Purpose: declares the main C++ LevelDB API: a persistent, concurrent ordered map from keys to values.

Important APIs and types: `kMajorVersion`, `kMinorVersion`, `Snapshot`, `Range`, abstract `DB`, static `DB::Open`, `Put`, `Delete`, `Write`, `Get`, `NewIterator`, `GetSnapshot`, `ReleaseSnapshot`, `GetProperty`, `GetApproximateSizes`, `CompactRange`, `DestroyDB`, and `RepairDB`.

Control flow: users open a DB with `Options`, perform writes and reads with per-operation options, create iterators/snapshots for stable views, ask for properties/size estimates, compact ranges, and delete/repair databases through free functions.

State and persistence behavior: the API abstracts WAL, MANIFEST, SSTable, snapshots, and compaction. `WriteOptions::sync` controls crash durability. Snapshots are immutable handles and must be released.

Dependencies and integration: includes iterator and options APIs. Implemented by `DBImpl` and connected to `VersionSet`, memtables, table cache, env, and write batches.

Risks and edge cases: iterators should be deleted before DB destruction. `DestroyDB` masks some listing failures for backward compatibility. `RepairDB` may lose data. `CompactRange` is advanced and can create latency spikes.

Test signals: nearly all DB tests exercise this API; issue tests in this subset target compaction, iterator snapshots, and snapshot-heavy write workloads.
