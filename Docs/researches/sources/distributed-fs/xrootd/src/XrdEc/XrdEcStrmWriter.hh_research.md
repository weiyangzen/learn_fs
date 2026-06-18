# sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.hh

## Purpose

This header declares `XrdEc::StrmWriter`, the asynchronous erasure-coded stream writer used by the XrdEc client layer. It accepts user writes, fills block-sized `WrtBuff` objects, schedules erasure coding and CRC calculation, and drains completed encoded blocks to data and metadata ZIP archives through XrdCl file/zip operations. It is the orchestration layer between the public write/open/close API and lower-level block encoding.

## Important APIs, Types, and Functions

The public API is `StrmWriter(const ObjCfg&)`, `~StrmWriter()`, `Open(ResponseHandler*, time_t)`, `Write(uint32_t, const void*, ResponseHandler*)`, `Close(ResponseHandler*, time_t)`, and `GetSize()`. `ObjCfg` supplies erasure layout and sizes, while user completion is reported through XrdCl `ResponseHandler` callbacks.

`buff_queue` is a `sync_queue<std::future<WrtBuff*>>`. `EnqueueBuff()` sends a raw `WrtBuff` pointer into `ThreadPool::Instance().Execute()` so `WrtBuff::Encode()` runs away from the caller. `DequeueBuff()` waits for the future and reclaims the pointer into a `unique_ptr`. `writer_routine()` is a dedicated consumer thread, and `WriteBuff()`, `GetMetadataBuffer()`, and `CloseImpl()` are the private write/close implementation hooks defined in the companion source.

`global_status_t` tracks outstanding bytes, committed bytes, the first non-OK status, close intent, and the saved close handler. It is protected by a recursive mutex and is shared by open/write/close callback paths.

## Control Flow

Construction starts the writer thread immediately. User `Write()` calls fill the current `WrtBuff`; full buffers are enqueued for background parity/checksum preparation. The writer thread blocks in `DequeueBuff()`, obtains an encoded buffer, and calls `WriteBuff()` to issue writes for the prepared stripes/archives.

Close is two-phase. `Close()` calls `global_status.issue_close()`, which marks that no more writes should arrive. If no bytes remain in flight, it calls `CloseImpl()` immediately; otherwise it saves the close handler and lets `report_wrt()` trigger `CloseImpl()` when outstanding writes reach zero.

Destruction sets `writer_thread_stop`, interrupts the queue, and joins the writer thread, which exits by catching `sync_queue::wait_interrupted`.

## State and Persistence Behavior

Persistent data is external: encoded chunks, metadata archive records, and central directory buffers are written through XrdCl ZIP/file objects. In-memory state includes the active write buffer, `dataarchs`, `metadataarchs`, `cdbuffs`, queued futures, `next_blknb`, and global byte/status counters.

The object keeps a reference to `ObjCfg`, so the configuration must outlive the writer. `global_status.status` retains failure state across callbacks, while `btswritten` is the size reported by `GetSize()`.

## Dependencies and Integration Points

The class depends on `XrdEcWrtBuff.hh`, `XrdEcThreadPool.hh`, `XrdClFileOperations`, `XrdClParallelOperation`, and `XrdClZipOperations`. It integrates with the XrdEc open/write/close implementation in the companion source and with XrdCl's asynchronous callback model.

## Risks and Edge Cases

The close path depends on every asynchronous write eventually calling `report_wrt()` with the same byte accounting used by `issue_write()`. A missed report can hang close; a double report can underflow `btsleft`. `get_btswritten()` is not mutex-protected even though updates are protected. The destructor interrupts the local queue but cannot cancel already running thread-pool encode jobs.

## Test Signals

Useful tests exercise partial-block writes, full-block writes, close while writes are outstanding, write failures before close, destructor during an idle dequeue, and byte-count accounting. Integration tests should verify generated ZIP metadata and data archives are readable by the matching XrdEc reader.
