# sources/storage-engines/rocksdb/db/db_with_timestamp_basic_test.cc

## Purpose
`db_with_timestamp_basic_test.cc` is RocksDB's broad behavioral test suite for user-defined timestamps (UDT) on ordinary DB operations. It verifies that timestamp-enabled column families enforce API contracts, that reads combine timestamp visibility with sequence-number and snapshot visibility, and that iterators, `Get`, `MultiGet`, range tombstones, merges, row cache, prefix filters, table timestamp metadata, history trimming, and `full_history_ts_low` all preserve correct time-travel semantics.

The file is intentionally integration-heavy. Most tests open real DB instances, write timestamped records, flush SSTs, compact across levels, reopen databases, and validate both returned values and returned key timestamps. It also exercises both persisted UDT mode and memtable-only UDT mode, where SST file boundaries and manifest metadata must compensate for stripped timestamps.

## Important APIs, Types, And Functions
`DBBasicTestWithTimestamp` is the main fixture and derives from `DBBasicTestWithTimestampBase`. It uses the helper `TestComparator`, which orders user keys by bytewise key and then orders timestamps in reverse timestamp order so newer timestamped versions sort before older versions for the same user key. `EncodeAsUint64()` is a local helper for the 8-byte timestamp mode used by RocksDB's built-in U64 timestamp wrapper.

Parameterized fixtures expand coverage across table and storage options:

- `DBBasicTestWithTimestampTableOptions` runs Get, MultiGet, seek, bound, and prefix tests across block-based index types.
- `DBBasicTestWithTimestampFilterPrefixSettings` combines Bloom filter policies, prefix extractors, memtable Bloom settings, whole-key filtering, cache-index/filter settings, and index types.
- `DBBasicTestWithTimestampCompressionSettings` combines compression algorithms, compression dictionaries, parallel compression threads, and filters.
- `DBBasicTestWithTimestampPrefixSeek` verifies prefix iteration over high unsigned-key ranges.
- `DBBasicTestWithTsIterTombstones` validates iterator behavior when timestamped deletions hide alternating keys.
- `DeleteRangeWithTimestampTableOptions` tests range tombstones under persisted and stripped UDT modes.
- `HandleFileBoundariesTest`, `EnableDisableUDTTest`, `DataVisibilityTest`, `UpdateFullHistoryTsLowTest`, and `GetNewestUserDefinedTimestampTest` focus on specific cross-cutting contracts.

The key RocksDB APIs under test include timestamped `Put`, `Merge`, `Delete`, `SingleDelete`, `DeleteRange`, `WriteBatch::UpdateTimestamps`, `Get` overloads returning key timestamps, all major `MultiGet` overloads, `NewIterator`, `NewIterators`, snapshots, `CompactRange`, `CompactFiles`, `IncreaseFullHistoryTsLow`, `GetFullHistoryTsLow`, `GetNewestUserDefinedTimestamp`, `DB::OpenAndTrimHistory`, `GetApproximateSizes`, `GetApproximateMemTableStats`, `GetPropertiesOfAllTables`, row cache, prefix Bloom filters, block-based table index types, and merge operators.

## Control Flow
The opening API tests establish legal and illegal combinations. Timestamped writes on a non-UDT column family must fail, non-timestamped writes on a UDT column family must fail, wrong-sized timestamps must fail, and `WriteBatch::UpdateTimestamps()` must allow mixed column-family batches when the timestamp-size callback returns the correct size per CF. Mixed-CF tests then close and reopen the DB to verify timestamped data survives manifest/recovery paths.

Lookup and iteration tests build multiple timestamped versions of each key and read at later timestamps. They verify forward and reverse scans, direction changes, `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, explicit key lower/upper bounds, `iter_start_ts`, `max_sequential_skip_in_iterations`, and reseek ticker accounting. The iterator tests intentionally cover cases where internal timestamp skipping must reseek to a target timestamp, a next user key, or a user key before a saved key.

`DataVisibilityTest` adds sequence-number visibility to timestamp visibility. It uses sync points and writer threads to interleave reads with later writes and flushes. The expected rule is that a record is visible only when both its user timestamp is at or below the read timestamp and its sequence number is visible to the read's implicit or explicit snapshot. The tests repeat this for point lookup, range scan, MultiGet, snapshots, no snapshots, and cross-column-family MultiGet.

History-management tests cover `full_history_ts_low`, `OpenAndTrimHistory`, compaction with `CompactRangeOptions::full_history_ts_low`, and public `IncreaseFullHistoryTsLow`. They verify increasing the low watermark, rejecting decreasing/empty/wrong-sized low timestamps, rejecting partial-range compactions with `full_history_ts_low`, preserving the latest version below the low watermark, collapsing timestamps to minimum timestamps when history is compacted, and returning `InvalidArgument` when a read timestamp falls below the SuperVersion's low watermark.

Table and filter tests flush and compact data under multiple block-based table index types, Bloom configurations, compression modes, prefix extractors, and row-cache setups. They verify `Get`, `MultiGet`, and iterators never treat timestamp suffix bytes as part of user-key prefixes or row-cache keys incorrectly. `TimestampFilterTableReadOnGet` specifically checks timestamp min/max file metadata can skip table reads and increments `TIMESTAMP_FILTER_TABLE_CHECKED` and `TIMESTAMP_FILTER_TABLE_FILTERED` tickers.

Delete, range tombstone, and merge tests validate timestamp semantics for `Delete`, `SingleDelete`, `DeleteRange`, and merge operands. They cover preserving range tombstones when no or too-small `full_history_ts_low` is set, dropping covered keys and tombstones only when the low watermark allows it, correct key timestamps in `Get` and `MultiGet` NotFound results, snapshot interactions with range tombstones, and merge results/timestamps across put-then-merge and delete-then-merge histories.

UDT mode transition tests write data without timestamps, reopen the same DB with timestamp support enabled, read old data as if it had minimum timestamps, write timestamped data with UDT stripped from SSTs, reopen with UDT disabled, and continue ordinary reads/writes. File-boundary tests inspect `FileMetaData` after reopen to ensure manifest encoding pads stripped boundaries with min or max timestamps as appropriate, including range-deletion sentinel boundaries.

## State And Persistence Behavior
This file treats timestamp support as both a logical read feature and a persisted storage-format feature. Flushes create SSTs whose internal keys, table properties, file boundaries, and timestamp min/max metadata must match the configured UDT mode. Compactions may drop expired history, zero sequence numbers, collapse timestamps to the minimum timestamp, or preserve tombstones depending on `full_history_ts_low` and bottommost-level state.

Snapshot and sequence state is part of the tested persistence model. A timestamp alone is not enough to make a newer write visible if the reader captured an older sequence number. Snapshot tests use sync points to make this race deterministic and confirm `Get`, iterators, and all `MultiGet` paths use a consistent sequence snapshot.

The suite also validates manifest and reopen behavior. `OpenAndTrimHistory` rewrites history during open and must preserve the correct value or tombstone visible at the trim timestamp. File-boundary tests close and reopen to ensure the manifest records either real timestamped boundaries or timestamp-stripped boundaries that are reconstructed with min/max timestamps. `GetNewestUserDefinedTimestamp` verifies newest UDT tracking through mutable memtables, immutable memtables, flush, manifest persistence, and reopen when timestamps are not persisted in SST user keys.

Row cache state is timestamp-sensitive. The tests deliberately mix `Get` calls with and without returned key timestamps and with different snapshots/read timestamps, expecting cache hits only when the cached entry is valid for the same logical visibility constraints and expecting the cached entry to carry the correct returned timestamp.

## Dependencies And Integration Points
The test depends on `db/db_with_timestamp_test_util.h` for timestamp encoding, timestamp-aware comparator behavior, and iterator assertions. It integrates with `db/db_test_util.h` through the base fixture for DB lifecycle, flushing, compaction helpers, snapshots, CF helpers, and file movement. It uses `test_util/sync_point.h` for deterministic concurrency, `rocksdb/perf_context.h`, `rocksdb/utilities/debug.h`, block-based table internals, `utilities/fault_injection_env.h`, and the string append test merge operator.

Integration points include RocksDB public DB APIs, `ColumnFamilyHandleImpl`/`ColumnFamilyData` internals for `full_history_ts_low` and memtable switching, `VersionEdit` sync points for concurrent low-watermark updates, table-property collectors for timestamp min/max, block-based table readers/builders, Bloom filters, prefix extractors, compression libraries, row cache statistics, iterator reseek statistics, and range tombstone sentinels.

## Risks
The highest-risk area is the interaction between user timestamp ordering and RocksDB's internal sequence ordering. Many tests rely on the comparator ordering timestamped versions in reverse timestamp order and on reads additionally filtering by sequence visibility. Bugs here can return future data to a snapshot, skip visible older versions, or report the wrong key timestamp with a value or tombstone.

`full_history_ts_low` is another correctness-sensitive boundary. If the low watermark is applied too aggressively, reads below a still-valid SuperVersion can become inconsistent or history can be dropped too early. If applied too conservatively, compaction can retain obsolete history or repeatedly compact bottommost files. The tests cover both invalid read rejection and read consistency when the SuperVersion still contains the needed history.

Persisted-vs-stripped UDT mode is subtle. When timestamps are stripped from SST user keys, manifest file boundaries and table timestamp metadata must still allow correct reads, compactions, and tombstone handling. Boundary padding with min/max timestamps and range tombstone sentinel encoding are easy places for off-by-one or comparator errors.

Prefix filtering, row cache, and MultiGet fast paths can accidentally use raw user keys including timestamp bytes, or omit timestamp/snapshot state from cache/filter decisions. The suite stresses these paths with multiple API overloads, long keys, prefix extractors, Bloom filters, and index types.

## Test Signals
Primary pass signals are exact `OK`, `NotFound`, `InvalidArgument`, `TryAgain`, and `NotSupported` statuses; exact values and returned key timestamps for `Get`, `MultiGet`, and iterators; preserved or collapsed timestamps after compaction; expected iterator validity at bounds; expected reseek and row-cache ticker deltas; expected table timestamp properties; expected file metadata boundaries after reopen; and correct behavior across persisted and stripped UDT modes.

High-value regression signals include a future write becoming visible to an older snapshot, a timestamped tombstone returning an empty or wrong tombstone timestamp, failure to reject reads below `full_history_ts_low`, compaction dropping range tombstones too early, `MultiGet` overloads disagreeing, row-cache hits returning values for the wrong timestamp/snapshot, prefix filters missing timestamped keys, and `GetNewestUserDefinedTimestamp` losing state across memtable switch, flush, or reopen.
