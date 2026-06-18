## sources/distributed-fs/xrootd/src/XrdEc/XrdEcStrmWriter.cc

### Purpose
This file implements the streaming writer for XrdEc objects. It opens placement archives, buffers user writes into erasure-code blocks, asynchronously encodes/checksums blocks, writes stripe zip entries across shuffled servers with retry, writes metadata or xattrs at close, and reports final status through XrdCl handlers.

### Important APIs, Types, and Functions
- `StrmWriter::Open` opens a `ZipArchive` for each placement in new/write mode and requires all `nbchunks` archives.
- `Write` appends user bytes into `WrtBuff` objects and enqueues complete blocks for encoding while reporting immediate user success after buffering.
- `Close` enqueues partial final data and delegates close sequencing to `global_status`.
- `WriteBuff` writes one encoded block's stripe entries as zip files named by `ObjCfg::GetFileName`, shuffling server placement and retrying failed stripe writes on other servers.
- `GetMetadataBuffer` packages each data archive's central directory into a metadata zip-like buffer with LFH/CDFH/EOCD records.
- `CloseImpl` sets xattrs, closes data archives, and optionally replicates metadata files.

### Control Flow
Open creates all archive objects and sends parallel open requests. Write first checks global error state, increments outstanding byte count, fills the current `WrtBuff`, and when a buffer becomes complete, passes it to `EnqueueBuff` from the header, where a thread-pool task encodes parity and CRCs. A dedicated writer thread dequeues prepared buffers and calls `WriteBuff`.

`WriteBuff` shares one prepared buffer across all stripe write pipelines, randomizes server order for block placement, builds one append operation per stripe, retries failed appends on an unused server, and reports the data-byte count for the block to `global_status` after all writes complete. Close marks no more writes, waits through `global_status` until outstanding bytes are reported, then runs `CloseImpl`. In metadata-file mode, `CloseImpl` closes all data archives and writes replicated metadata to at least `nbparity + 1` placements; in no-metadata mode it sets `xrdec.filesize` and `xrdec.strpver` xattrs and closes data archives only.

### State and Persistence
Persistent outputs are remote data zip archives containing stripe entries, optional `.mt` metadata files holding central-directory summaries, and xattrs recording file size and stripe version. Runtime state includes data/metadata archive vectors, current write buffer, queue of futures for prepared buffers, background writer thread, next block number, and global write/close status.

### Dependencies and Integration Points
The implementation depends on `XrdEcStrmWriter.hh`, `WrtBuff`, `ThreadPool`, XrdCl zip/file/parallel operations, XrdZip LFH/CDFH/EOCD helpers, and `ObjCfg`. `XrdClEcHandler` constructs this writer for EC file writes.

### Risks and Edge Cases
`Write` reports success once data is buffered, so later remote write failures surface only through subsequent writes or close. `Open` invokes `handler->HandleResponse` without null-checking `handler`. `WriteBuff` retries failed appends but if no alternate server remains, the lambda returns without directly reporting that stripe failure; final parallel status behavior must be verified. The random engine is static and shared. `global_status_t::report_wrt` subtracts from unsigned `btsleft`, so mismatched byte accounting can underflow. Close handler timeout is not preserved when deferred in `issue_close`. Background-thread shutdown depends on queue interrupt and join.

### Test Signals
Tests should cover open success/failure thresholds, writes smaller/larger than one block, partial final block close, server shuffle and retry, failed writes surfacing at close, metadata-file contents parseable by `Reader::ParseMetadata`, no-metadata xattrs, background thread shutdown, and concurrent write/close ordering.
