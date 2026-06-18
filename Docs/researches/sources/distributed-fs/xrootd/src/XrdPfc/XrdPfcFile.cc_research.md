# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.cc

## Purpose
Implements `XrdPfc::File`, the central block cache object for the proxy file cache. It opens/creates local data and `.cinfo` metadata files, coordinates concurrent read requests, downloads missing blocks from remote `XrdOucCacheIO`, writes completed blocks to disk, persists block state, reports usage to `ResourceMonitor`, and drives prefetch.

## Important APIs, Types, and Functions
- `File::FileOpen()` constructs and opens a `File`, returning null on local open or metadata setup failure.
- `Open()` creates/opens the local data file and `.cinfo`, validates existing metadata/data consistency, applies checksum and URL CGI configuration, initializes access statistics, and registers the open with `ResourceMonitor`.
- `Close()` closes local handles, reconciles final `st_blocks`, and registers file close.
- `Read()` and `ReadV()` are the public entry points used by `IOFile`; complete files take a direct local disk fast path.
- `ReadOpusCoalescere()` is the main cache read planner: it splits user I/O into blocks, classifies chunks as RAM, disk, remote-cacheable, or direct remote bypass, issues asynchronous remote requests, and returns either bytes/error or `-EWOULDBLOCK`.
- `PrepareBlockRequest()`, `ProcessBlockRequest()`, `ProcessBlockResponse()`, `ProcessBlockSuccess()`, and `ProcessBlockError()` manage in-flight `Block` lifecycle.
- `WriteBlockToDisk()` writes downloaded blocks into the local data file, updates `Info` bitmaps, and schedules `Sync()`.
- `Sync()` fsyncs data, writes and fsyncs `.cinfo`, records access stats, and initiates emergency unlink/shutdown on sync failure.
- `Prefetch()` picks the next missing block and issues asynchronous fetches under prefetch flow control.
- `ioActive()`, `AddIO()`, `RemoveIO()`, `RequestSyncOfDetachStats()`, and `FinalizeSyncBeforeExit()` coordinate detach and final metadata flush.

## Control Flow
Open flow first waits for `ResourceMonitor` initial scan cross-check, creates data and metadata files in configured data/meta spaces, reads existing `.cinfo` if present, truncates/reset metadata when data size, checksum policy, or uvkeep rules make cached contents invalid, and registers an access record. Read flow locks `m_state_cond`, rejects shutdown/detaching IO, fast-paths complete files, otherwise walks requested blocks. Existing RAM blocks are refcounted, disk blocks are coalesced into local `ReadV`, missing blocks allocate RAM and remote reads, and RAM pressure causes direct remote `ReadV` bypass. Completion is split between synchronous disk/RAM work and asynchronous callbacks. Block callback flow writes successful downloads to disk through the cache write queue, notifies all waiting chunk requests, reissues failed blocks through another IO when possible, and finalizes read callbacks once all chunk/direct/sync parts complete.

## State and Persistence Behavior
Persistent state is split between the local data file and `Info` metadata file with extension `.cinfo`. `Info` tracks written/synced/prefetched block bitmaps, file size, block size, checksum mode, and access history. `File` maintains transient state in `m_block_map`, `m_io_set`, ref counts, write/sync counters, prefetch state, remote locations, and resource-monitor deltas. `Sync()` is the durability boundary: data is fsynced before `.cinfo` is updated so metadata does not advertise unsynced blocks. Emergency shutdown prevents further writes and causes future reads to return `-ENOENT`.

## Dependencies and Integration Points
Integrates with `Cache` for active-file lifetime, RAM allocation, write queue, sync scheduling, purge protection, config, xattrs, and remote cache-control storage. Uses `ResourceMonitor` tokens for open/update/close accounting. Uses `XrdOss` for local file operations, `XrdOucCacheIO` for remote reads, `XrdOucIOVec` and `XProtocol` limits for vector read chunking, `XrdCl::URL` for CGI options, and `XrdPfc::Info`/`Stats`/trace macros for metadata and diagnostics.

## Risks and Test Signals
High-risk areas are concurrency around `m_state_cond`, refcount/free ordering between read callbacks and write queue callbacks, recursive `Sync()` under writes-during-sync, and error recovery that unlinks active files. Other risks include wrong offset math for block-based files (`m_offset`), stale `.cinfo` acceptance, direct-read fallback when RAM is exhausted, and checksum downgrade/reset behavior. Strong tests should cover partial reads across block boundaries, concurrent ReadV against same missing block, failed remote reads with reissue through a second IO, sync failure unlink, prefetch stop/hold/complete transitions, CGI blocksize/prefetch parsing, and restart from existing `.cinfo` plus truncated data.
