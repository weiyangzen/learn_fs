<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable.cc -->
# sources/storage-engines/rocksdb/db/memtable.cc

## Purpose
Implements RocksDB's mutable and immutable memtable behavior: memory allocation and flush triggers, point/range entry insertion, iteration, range tombstone fragmentation, gets and multigets, merge processing, in-place updates, blob/wide-column handling, per-entry checksum protection, timestamp-aware iteration, and WAL prepare-section tracking.

## Important APIs, Types, And Functions
`ImmutableMemTableOptions` snapshots immutable/mutable column-family options relevant to memtable behavior. `ReadOnlyMemTable::ProtectSealedBlobFiles()` and `ReleaseProtectedSealedBlobFiles()` protect blob files referenced by immutable memtables. `MemTable::MemTable()` constructs arena-backed point and range-deletion memtable reps, bloom filters, cached range-tombstone state, and timestamp metadata. Memory/flush APIs include `ApproximateMemoryUsage()`, `ShouldFlushNow()`, `UpdateFlushState()`, and `UpdateOldestKeyTime()`.

Insertion and validation center on `Add()`, `VerifyEntryChecksum()`, `VerifyEncodedEntry()`, and `UpdateEntryChecksum()`. Read paths include `NewIterator()`, `NewTimestampStrippingIterator()`, `NewRangeTombstoneIterator()`, `NewRangeTombstoneIteratorInternal()`, `ConstructFragmentedRangeTombstones()`, `Get()`, `GetFromTable()`, and `MultiGet()`. Mutation helpers include `Update()`, `UpdateCallback()`, `CountSuccessiveMergeEntries()`, `AddLogicallyRedundantRangeTombstone()`, and `BumpIngestSeqnoBarrier()`. Tail helpers track prepared WAL refs and newest user-defined timestamp.

Internal helper classes/functions include `MemTableIterator`, `TimestampStrippingIterator`, `Saver`, `SaveValue()`, wide-column/blob merge helpers, `EncodeKey()`, and `MemTableRep::Get()`/`MultiGet()`.

## Control Flow
Construction builds the point table from the configured memtable factory and the range-deletion table from a concurrent skip list. `Add()` encodes entries as `varint32 internal_key_len | user_key | packed seq/type | varint32 value_len | value | optional checksum`, inserts into the point or range table, updates counters, bloom filters, sequence bounds, newest timestamp, flush state, and range-tombstone caches. Concurrent insertion defers counter aggregation through `MemTablePostProcessInfo`.

Read paths first account for range tombstones, then use bloom filters when safe, then seek the memtable rep and invoke `SaveValue()` for entries with the target user key. `SaveValue()` enforces callback visibility, verifies checksums, applies covering range tombstones, handles value/blob/wide-column/delete/merge types, and either returns a final value/status or continues gathering merge operands. `MultiGet()` can batch memtable lookups after range tombstone handling and bloom filtering, then marks completed keys and enforces `value_size_soft_limit`.

Iterator paths wrap memtable rep iterators, optionally use prefix bloom/dynamic prefix iterators, validate entries on seek/next when configured, expose write time via `SeqnoToTimeMapping`, and optionally strip timestamps from internal keys/range tombstone values. Range tombstone reads build cached fragmented lists for mutable memtables and precomputed lists for immutable memtables.

## State And Persistence Behavior
Memtables are in-memory, arena-allocated write buffers, but they are the live source for reads before flush and determine what later persists to SSTs. State includes entry/data/delete/range-delete counters, arena memory, approximate memory usage, bloom filters, first/earliest sequence numbers, creation sequence, oldest key time, cached fragmented tombstone lists, immutable flag, ingest sequence barrier, protected blob file references, prepared-WAL minimum reference, and newest UDT pointer. Flush state changes when memory/range-delete thresholds are reached or explicitly marked.

## Dependencies And Integration Points
This file integrates with internal key format, comparators, merge operators, wide-column serialization, blob fetching and blob-file partition protection, range tombstone fragmentation, `MemTableRep` factories, write buffer management, arena allocation, perf counters/statistics, read callbacks, prefix extractors, pinned iterators, sequence-to-time mapping, protection checksums, and transaction/WAL retention. It is a central bridge between DB write batches, read paths, flush, compaction, blob GC safety, and timestamp-aware features.

## Risks And Edge Cases
Correctness depends on byte-format consistency between `Add()`, `SaveValue()`, iterators, and checksum validation. Range tombstone cache invalidation must be thread-safe with readers. Bloom filters are disabled or narrowed in multiget when range tombstones are present to avoid false negative deletion behavior. In-place updates must preserve existing sequence numbers and update checksum state correctly. Wide-column default values may be blob-backed and require a blob fetcher; missing fetchers become corruption/not-supported outcomes. The ingest sequence barrier prevents logically redundant tombstones from invalidating assumptions around externally ingested files. Timestamp stripping must preserve comparator semantics while hiding UDT bytes from downstream consumers.

## Test Signals
Coverage comes from RocksDB DB, memtable, merge, range tombstone, timestamp, blob, write-buffer, corruption/protection, and transaction tests. Sync points include `MemTable::Add:Encoded`, `MemTable::Add:BeforeReturn:Encoded`, `Memtable::SaveValue:Found:entry`, `MemTableIterator::Next:0`, and `MemTable::AddLogicallyRedundantRangeTombstone:AddRange`. Failures typically show as missed reads, incorrect merge results, flush timing regressions, range tombstone visibility bugs, checksum corruption reports, or WAL-retention mistakes for prepared transactions.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/memtable.cc -->
