# sources/storage-engines/tikv/components/compact-log-backup/src/cache.rs

## Purpose
Implements a bounded, sharded in-memory cache for raw physical log files. It lets multiple logical log spans share one downloaded physical object and returns zero-copy `Bytes` slices to compaction workers.

## APIs and control flow
`PhysicalFileCache::new` sets capacity, reservation counter, notify channel, and 256 mutex-protected shards. `register_physical_file` reserves capacity and records reference counts, returning `Registered`, `Full(wait)`, or `Bypass`. `load_part` loops over `cache_decision`: ready returns a slice, wait awaits another downloader, bypass asks caller to read directly, and download loads the full physical file then publishes it. `DownloadGuard` clears `loading` and notifies waiters if a download future is cancelled. `PhysicalFileCacheRefGuard` drops physical-file refs on `Drop`; when refs hit zero, entries are removed and reserved capacity is released.

## State, dependencies, and integration
State is entirely in-memory: per-shard `HashMap<Chars, CacheEntry>`, atomic `reserved_bytes`, notify objects, content bytes, loading flags, and remaining refs. It depends on `external_storage`, `cloud::blob::read_to_end`, `bytes`, `parking_lot`, Tokio notify futures, protobuf `Chars`, and compaction `Input`. It integrates with cached subcompaction collection and `Source` loading.

## Risks and test signals
Reference accounting must match logical input consumption; early drops can release reservations while slices still live, although `Bytes` keeps allocation alive. Full-file downloads can allocate `physical_size` capacity and require valid offset/length ranges. Tests cover cancelled-download loading cleanup and reservation release after both cached parts are consumed.
