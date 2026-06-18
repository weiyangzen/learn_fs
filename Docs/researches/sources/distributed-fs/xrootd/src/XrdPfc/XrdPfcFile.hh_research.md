# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcFile.hh

## Purpose
Declares the core proxy-cache file model and its read/block helper types. The header exposes the `File` API used by cache IO adapters while hiding local file handles, metadata state, block map, sync machinery, and prefetch internals.

## Important APIs, Types, and Functions
- `ReadReqRH`: internal callback wrapper carrying expected size, read sequence id, chunk count, and the external callback.
- `ReadRequest`: aggregate state for a logical read spanning disk, RAM, remote block, and direct remote sub-requests.
- `ChunkRequest`: maps a requested byte range within a block to the final user buffer and owning `ReadRequest`.
- `Block`: transient in-memory block with remote IO identity, buffer, offset/size, refcount, checksum vector, status, and pending chunk requests.
- `BlockResponseHandler` and `DirectResponseHandler`: callback adapters from remote reads back into `File`.
- `File`: public operations include `FileOpen`, `Read`, `ReadV`, `Sync`, `WriteBlockToDisk`, `Prefetch`, `Fstat`, IO attach/detach helpers, resource-monitor accessors, and emergency shutdown.

## Control Flow
The header defines a layered async model. IO adapters create `ReadReqRH` objects and call `File::Read`/`ReadV`. `File` creates `ReadRequest` only when asynchronous work is needed. Each missing or in-flight block receives `ChunkRequest` entries, while callback handlers call back into `File` to update block and read-request state. Inline `inc_ref_count`/`dec_ref_count` are always intended to run under `m_state_cond`, and `dec_ref_count` frees completed blocks when the last user/write-queue reference drops.

## State and Persistence Behavior
Persistent metadata is encapsulated in `Info m_cfi`; local persistence handles are `m_data_file` and `m_info_file`. Transient state includes active IO set, current prefetch IO, writes-during-sync vector, non-flushed count, block map, resource-monitor stats/deltas, remote locations, and prefetch score counters. The header makes the state invariants explicit: blocks may be freed only after finished and refcount zero, and sync state separates written from synced metadata.

## Dependencies and Integration Points
Depends on `XrdPfcTypes.hh`, `XrdPfcInfo.hh`, `XrdPfcStats.hh`, `XrdOucCache.hh`, and `XrdOucIOVec.hh`. It forward-declares `IO` and callback types to avoid circular includes. It is the primary contract between `Cache`, `IOFile`, `IOFileBlock`, remote `XrdOucCacheIO`, and resource monitoring.

## Risks and Test Signals
The main risks are ownership ambiguity for `ReadReqRH` and `ReadRequest`, callback ordering, and refcount misuse. Tests should stress callback completion ordering, block free after write queue removal, detach while reads/prefetches are active, and all paths where `ReadRequest::is_complete()` transitions from false to true.
