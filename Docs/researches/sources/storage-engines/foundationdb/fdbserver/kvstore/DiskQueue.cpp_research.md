# sources/storage-engines/foundationdb/fdbserver/kvstore/DiskQueue.cpp

## Purpose
`DiskQueue.cpp` implements FoundationDB's `IDiskQueue` durable append/read/pop queue on top of two asynchronously accessed files. It is the low-level persistence log used by the in-memory key-value store and log-system testing paths. The core design is a dynamically resizable two-file ring buffer: one file is logically older, the other is the active append target, and the implementation swaps/truncates/replaces files as data is popped and space can be reclaimed.

## Important APIs, Types, and Functions
The exported entry point is `openDiskQueue(...)`, which returns `DiskQueue_PopUncommitted`, a wrapper around `DiskQueue` that guards against popping data beyond the committed point. `DiskQueue` implements `IDiskQueue` methods: `push`, `pop`, `commit`, `read`, `initializeRecovery`, `readNext`, `getNextReadLocation`, `getNextPushLocation`, `getCommitOverhead`, `dispose`, and `close`. `RawDiskQueue_TwoFiles` owns the two `IAsyncFile` handles, file sizes, popped offsets, page buffers, and file open/truncate/swap logic. `StringBuffer` provides arena-backed aligned append buffers. `SyncQueue` serializes file sync futures so a commit waits for all writes that preceded its sync request.

## Control Flow
Writes accumulate in `DiskQueue::pushed_page_buffer` as fixed-size 4 KiB pages with a packed `PageHeader`. `push()` copies payload bytes into page payloads, allocating new pages as needed. `commit()` seals the last page by storing the current durable pop point, zero-padding unused payload bytes, computing the page checksum, then delegates to `RawDiskQueue_TwoFiles::pushAndCommit()`. The raw queue serializes push order through `readyToPush`, writes pages to file 1, extends or swaps files if necessary, syncs all touched files, waits for the previous commit, then advances durable popped bytes. Recovery orders the two files by first page sequence number, binary-searches the active file for the last valid page, then streams pages until EOF or an invalid page.

## State and Persistence Behavior
The on-disk unit is `DiskQueue::Page`, exactly `_PAGE_SIZE`, with sequence number, popped location, payload size, implementation version, magic, and checksum. Versions select legacy `hashlittle2`, CRC32C, or XXH3 checksums; new queues use V2. Durable deletion is represented by committing a page whose `popped` field names the safe pop point. Opening is strict: both queue files must exist or neither must exist. Creation uses atomic write/create flags followed by sync.

## Dependencies and Integration Points
This file depends on `IDiskQueue.h`, `IAsyncFile`, Flow actors/futures, simulator hooks, server knobs, CRC32C, XXHash, and trace/probe infrastructure. It is integrated by `KeyValueStoreMemory.cpp` for mutation-log storage and by any component opening an `IDiskQueue`.

## Risks
The main correctness risks are crash recovery, page checksum compatibility, async lifetime, and the historical issue of popping uncommitted data. The code uses raw pointers and self-deleting `dispose`/`close` actors, so `Tracked` coverage is important. File replacement/truncation is platform-specific, and partial page recovery relies on strict checksum and sequence ordering.

## Test Signals
The performance test opens a V2 queue, recovers it, pushes 10 MB values, reads older locations, pops, and pipelines commits. `CODE_PROBE`, `ASSERT`, `ASSERT_WE_THINK`, and `buggify()` branches exercise swaps, truncation, invalid pages, high page counts, and pop/commit edge cases.
