# sources/storage-engines/foundationdb/fdbserver/kvstore/KeyValueStoreSQLite.cpp

## Purpose

`KeyValueStoreSQLite.cpp` implements the legacy SQLite-backed FoundationDB `IKeyValueStore` variants for `.fdb` and `.sqlite` files. It bypasses normal SQL tables for hot-path storage and uses SQLite's internal btree APIs directly, with one blob-key table for encoded key/value records and one int-key free-page table for deferred deletion. It also owns FDB-specific database file creation, WAL checkpointing, asynchronous VFS integration, page checksum validation, value fragmentation for btree v2, spring-cleaning maintenance, file dump/check utilities, and the `keyValueStoreSQLite(...)` factory.

The implementation uses coroutine thread pools and a custom `VFSAsync` SQLite VFS to align SQLite file IO with Flow/FDB scheduling. One writer coroutine serializes all mutation, commit, checkpoint, lazy-delete, and vacuum work. Reader coroutines keep per-thread read cursors/snapshots that are reset by writer checkpoints.

## Important APIs, Types, and Functions

- `SpringCleaningStats` tracks counts and timings for lazy deletion, incremental vacuum, and spring-cleaning runs.
- `PageChecksumCodec` is a SQLite pager codec that stores/verifies an 8-byte checksum in each page reserve area. It writes xxHash3 checksums for new pages, reads legacy CRC32 and hashlittle2 formats, handles page-1 sizing special cases, logs checksum failures with simulator corruption context, and provides `codec`, `sizeChange`, and `free` callbacks for `sqlite3BtreePagerSetCodec`.
- `SQLiteDB` wraps a raw `sqlite3*`, `Btree*`, table root numbers, open DB/WAL `IAsyncFile` references, mutex ownership, checksum and fragmentation flags, and methods for opening, creating, transactions, WAL checkpointing, incremental vacuum, btree integrity checks, page checksum scans, and error translation.
- `Statement` is a small RAII wrapper around `sqlite3_stmt` used for PRAGMA setup and journal-mode validation.
- `encode`, `decodeKV`, `decodeKVPrefix`, and `encodeKey` encode FDB keys/values into SQLite record-compatible blob keys. `encodeKVFragment`, `decodeKVFragment`, and `getEncodedKVFragmentSize` implement `(key, index, value)` record format for optional value fragmentation.
- `SQLiteTransaction`, `IntKeyCursor`, `RawCursor`, and `Cursor` wrap low-level SQLite btree transactions and cursors. `RawCursor` is the core read/write cursor for movement, record extraction, insertion, deletion, fast range deletion, lazy deletion, point reads, prefix reads, and range scans.
- `RawCursor::DefragmentingReader` reassembles multiple fragments for a logical key during forward/reverse range reads and partial prefix reads.
- `ReadCursor` is a reference-counted lazily constructed read transaction/cursor. The writer clears `readCursors` before WAL checkpoints so readers move to fresh snapshots.
- `KeyValueStoreSQLite` is the `IKeyValueStore` implementation. Public methods include `set`, `clear`, `commit`, `readValue`, `readValuePrefix`, `readRange`, `getStorageBytes`, `getError`, `onClosed`, `close`, `dispose`, `doClean`, and `startReadThreads`.
- `KeyValueStoreSQLite::Reader` posts `ReadValueAction`, `ReadValuePrefixAction`, and `ReadRangeAction` to read coroutines. `Reader::getCursor()` rotates a cursor when `SQLITE_CURSOR_MAX_LIFETIME_BYTES` is exceeded.
- `KeyValueStoreSQLite::Writer` owns the writable `SQLiteDB`, active write `Cursor`, checksum/integrity-open checks, set/clear/commit actions, WAL checkpoints, read-cursor resets, free-page accounting, and spring-cleaning actions.
- Utility functions `createTemplateDatabase()`, `GenerateIOLogChecksumFile()`, `KVFileCheck()`, and `KVFileDump()` support template generation, IO-log checksum generation, offline validation, and dumping key/value files.

## Control Flow

Factory construction creates a `KeyValueStoreSQLite`, registers `vfsAsync()` once for coroutine SQLite use, asserts the DB and WAL paths are not already open, creates the writer coroutine first, posts a writer `InitAction`, starts readers only after writer initialization completes, and starts periodic cleaning and metric logging actors. `stopOnError()` monitors reader/writer pool errors, disables rate control, and stops both pools on non-cancellation failure.

`SQLiteDB::open(writable)` first opens or creates the database and WAL files through `IAsyncFileSystem`, ensuring a WAL file is created and synced before creating a new database file. New database bytes come from `template_fdb_with_page_checksums`, `template_fdb_without_page_checksums`, or the corresponding template path by store type. It configures optional write rate control, opens SQLite through `sqlite3_open_v2`, sets file chunk size, initializes the pager checksum codec, requires WAL journal mode, sets `synchronous = NORMAL` and disables auto-checkpoint for writers, enters the SQLite mutex, records table root pages 3 and 4, and stores DB/WAL async file references.

Writer initialization optionally scans every page checksum before opening the writable DB, opens the DB, publishes file references to the store, performs a full checkpoint to clean up any WAL left by a previous crash, creates the writable cursor, and optionally runs `sqlite3BtreeIntegrityCheck`.

Mutations are asynchronous actions on the writer pool. `set()` posts `Writer::SetAction`, which checks free pages and writes via `RawCursor::set()`. In non-fragment mode, this seeks the exact key, deletes any existing row, encodes `(key,value)`, and inserts. In fragment mode, it deletes all current fragments for the key, calculates whether fragmentation saves enough overflow-page waste using `SQLITE_FRAGMENT_*` knobs, then inserts one `(key,0,value)` record or multiple increasing index fragments.

`clear()` posts `Writer::ClearAction`, which first calls `fastClear()` to free btree pages for the range into a buffer and record them in the free-page table via `sqlite3BtreeLazyDelete`, then calls slower row-by-row `clear()` to remove remaining logical records or fragments. `commit()` posts `Writer::CommitAction`; the writer commits the btree transaction, destroys the cursor, performs a full WAL checkpoint and restart checkpoint while no cursor transaction is open, sends completion, opens a new write cursor, refreshes free-page counters, and updates `diskBytesUsed`.

Reads are posted to reader coroutines. Each reader lazily creates or refreshes a `ReadCursor` transaction. `readValue` seeks to a key and either returns the decoded row, an unfragmented `(key,0)` fragment, or defragments adjacent fragments. `readValuePrefix` reads enough encoded bytes to decode only the requested value prefix, including partial fragment handling. `readRange` supports forward and reverse limits; fragment mode uses `DefragmentingReader` to return logical key/value pairs while non-fragment mode decodes each btree row directly. `RangeResult::more` is based on row/byte limit exhaustion.

Spring cleaning runs periodically through `cleanPeriodically()` and `Writer::SpringCleaningAction`. It interleaves lazy deletion from the free-page table with incremental vacuum work under knob-controlled time and page budgets, updates free-list pages, records timing/counter metrics, yields inside the loop, and schedules the next cleaning interval based on whether work was performed.

Close/dispose disables rate control and wakes waiters, cancels startup/cleaning/logging actors, stops read and write pools, optionally incrementally deletes the DB and WAL files, signals `onClosed`, and deletes the store.

## State and Persistence Behavior

Persistent state is stored in a SQLite database file plus `-wal` file. The btree table at root page 3 stores encoded key/value records. The free table at root page 4 stores pages pending lazy deletion. Auto-vacuum is enabled by template/database creation, WAL mode is required, and writer commits are followed by explicit full and restart checkpoints rather than SQLite auto-checkpointing.

For btree v1 (`SSD_BTREE_V1` / `.fdb`), page checksums and value fragmentation are disabled. For btree v2 (`SSD_BTREE_V2` / `.sqlite`), constructor arguments pass `is_btree_v2` to `SQLiteDB`, enabling page checksums and value fragmentation. Page checksums reserve `sizeof(PageChecksumCodec::SumType)` bytes at the end of each page. New writes use xxHash3, while reads remain compatible with CRC32 and hashlittle2 historical formats.

The in-memory store tracks request/completion counters, read cursor references, writer/read thread pools, active DB and WAL file references, spring-cleaning stats, current disk bytes used, current SQLite free-list pages, and actor futures for startup, cleaning, logging, and stop-on-error. Writer state includes an active transaction cursor, commit count, set count, free-table-empty hint, and references to read-cursor slots.

`getStorageBytes()` reports filesystem free/total bytes for the parent directory, `diskBytesUsed` from DB plus WAL sizes, and available bytes adjusted by `_PAGE_SIZE * freeListPages`, treating free-list pages as reclaimable capacity.

## Dependencies and Integration Points

The file integrates with SQLite internals (`sqliteInt.h`, btree cursor APIs, pager codec hooks, WAL checkpoint APIs, `sqlite3VdbeSerialGet`, `sqlite3BtreeDeleteRange`, `tryReadEveryDbPage`) and therefore depends on the bundled/amalgamated SQLite internals remaining compatible with these calls. It defines `SQLITE_THREADSAFE 0` and no-ops SQLite mutex macros in that build mode, while still using explicit `sqlite3_mutex_enter/leave` wrappers.

FoundationDB integration points include `IKeyValueStore`, `IAsyncFileSystem`, `IAsyncFile`, `VFSAsync`, `CoroThreadPool`, `TraceEvent`, `SERVER_KNOBS`, `FLOW_KNOBS`, `TaskPriority::DiskRead/DiskWrite`, simulation fault injection, `KVFileUtils`, `template_fdb.h`, `NativeAPI.actor.h` printable/unprintable helpers, and Flow actors for periodic cleaning/logging/close.

Operational utilities `KVFileCheck()` and `KVFileDump()` construct the same store implementation for offline verification and dumping. `GenerateIOLogChecksumFile()` provides fixed-block hashlittle checksums for IO logs.

## Risks and Edge Cases

- The implementation uses SQLite private/internal APIs and raw btree structures, so it is sensitive to SQLite internal ABI or semantic changes.
- `SQLITE_THREADSAFE 0` and coroutine execution assume serialized access through the designed reader/writer pools and explicit mutex handling; unexpected cross-thread use would be unsafe.
- `RawCursor::clear()` is explicitly marked slow, and `ClearAction` currently performs both `fastClear()` and row-by-row `clear()` with a TODO "at most one".
- Fragmentation relies on index-size hints to allocate a reassembly buffer. Comments note that if index numbering changes or hints become inaccurate, asserts must be replaced by expandable-buffer logic.
- Page checksum behavior must support three algorithms. False inference from checksum marker bits is mitigated by fallback checks, but corruption logging and simulation injected-error mapping are complicated.
- `SQLiteDB::open()` has a path for a missing DB with present WAL that renames the WAL and asserts that this should not happen in current FoundationDB worker discovery.
- WAL checkpointing requires no outstanding writer cursor and forcibly resets read cursors; stale read cursor handling is central to correctness.
- `checkAllPageChecksums()` has an inline comment `REMOVE THIS BEFORE CHECKIN` around a missing-file early return, indicating a suspicious legacy/debug path.
- `checkError()` maps most SQLite errors to `io_error`, with special handling for injected simulation faults and OOM. Higher-level code may not get precise SQLite error classes.
- Store close deletes both DB and WAL incrementally on dispose, so callers must choose `close()` vs `dispose()` correctly.

## Test Signals

This file does not define local `TEST_CASE` blocks. Its behavior is typically exercised by FoundationDB storage-engine tests, simulation workloads, btree v1/v2 compatibility tests, corruption/injected fault tests, and file utility entry points.

Concrete built-in validation hooks include:

- `KVFileCheck(filename, integrity)`, which opens `.fdb` or `.sqlite` with either full btree integrity checking or full page checksum scanning and waits for initialization to complete.
- `SQLiteDB::checkAllPageChecksums()`, which locks DB/WAL files, installs the checksum codec silently, scans pages via `tryReadEveryDbPage`, and logs corrupt/read-failed pages up to `SQLITE_PAGE_SCAN_ERROR_LIMIT`.
- `SQLiteDB::check(verbose)`, which calls `sqlite3BtreeIntegrityCheck` on pages 1, 3, and 4 and emits detailed trace lines.
- `CODE_PROBE`s for reading legacy checksum formats, lazy deletion, vacuuming, and mixed spring-cleaning branches.
- `DiskMetrics` and `SpringCleaningMetrics` trace events for read/write queue depths, operation counts, SQLite memory high water, cleanup counts, and cleanup timing.
