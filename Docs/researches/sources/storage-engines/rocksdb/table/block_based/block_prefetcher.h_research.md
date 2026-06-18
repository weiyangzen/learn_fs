## sources/storage-engines/rocksdb/table/block_based/block_prefetcher.h

Purpose: declares `BlockPrefetcher`, the per-iterator/per-reader helper that tracks sequential block access and owns optional file prefetch buffering.

Important APIs/types: constructor sets compaction readahead and initial auto readahead. Public methods are `PrefetchIfNeeded()`, `prefetch_buffer()`, `UpdateReadPattern()`, `IsBlockSequential()`, `ResetValues()`, and `SetReadaheadState()`. `SetReadaheadState()` imports persisted adaptive-readahead state from `ReadaheadFileInfo::ReadaheadInfo` and exposes a sync point for tests.

Control flow: callers update or query the object around block reads. `IsBlockSequential()` compares the next offset with `prev_offset_ + prev_len_`, treating the first read as sequential. `ResetValues()` restarts auto-read detection after a random access. `PrefetchIfNeeded()` performs the actual policy implementation in the `.cc` file.

State and persistence behavior: state is in-memory and bound to scanning/read behavior: compaction readahead, current/initial auto readahead, readahead limit, number of file reads, previous offset/length, and owned `FilePrefetchBuffer`. The `SetReadaheadState()` hook can restore adaptive readahead counters from file-level info but does not persist them itself.

Dependencies/integration points: includes `block_based_table_reader.h` for `BlockBasedTable::Rep`, file prefetch buffer types, block handles, and read options. It is used by block-based table iterators and compaction read paths.

Risks: object reuse without `ResetValues()` after access pattern changes can retain stale sequential state. The prefetch buffer pointer is exposed raw, so lifetime remains with the `BlockPrefetcher`.

Test signals: filesystem prefetch-support and MultiScan tests exercise call sites. Sync-point callback in `SetReadaheadState()` provides a targeted hook for adaptive-readahead tests outside this file.
