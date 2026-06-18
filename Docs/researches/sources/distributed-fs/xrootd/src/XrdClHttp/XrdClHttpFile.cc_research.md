# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.cc

## Purpose
`XrdClHttpFile.cc` implements the `XrdClHttp::File` plugin object, translating XrdCl file operations into asynchronous HTTP/curl operations. It covers open, close, stat, fcntl metadata, scalar reads, page reads, vector reads, sequential upload, full-download mode, prefetching, dynamic query parameters, header callouts, and monitoring counters.

## Important APIs and Functions
Public overrides implemented here include `Open`, `Close`, `Stat`, `Fcntl`, `Read`, `PgRead`, `VectorRead`, both `Write` overloads, `IsOpen`, `GetProperty`, and `SetProperty`. Important helpers include `ParseHeaderTimeout`, `GetHeaderTimeoutWithDefault`, `GetHeaderTimeout`, `GetMonitoringJson`, `ReadPrefetch`, `GetCurrentURL`, and `CalculateCurrentURL`.

Nested/anonymous handlers perform response transformations: `OpenResponseHandler` sets `m_is_opened`; `OpenFullDownloadResponseHandler` converts the first full-download `ReadResponseInfo` into `OpenResponseInfo`; `PgReadResponseHandler` converts `ChunkInfo` to `PageInfo` with CRC32C page checksums; `CloseCreateHandler` handles zero-byte object creation; `PrefetchResponseHandler` chains sequential reads on one GET; `PrefetchDefaultHandler` disables failed/expired prefetch; `PutResponseHandler` serializes writes on one PUT; `PutDefaultHandler` records upload failures; and the default header callout injects `Content-Length` for known-size PUT.

## Control Flow
`Open` parses the URL, handles a special no-op plugin-loading open, normalizes `xrdclhttp.timeout` and `oss.asize`, initializes prefetch state, and either starts a full-object GET or a `CurlOpenOp`. `Read`/`PgRead` try the sequential prefetch path first, fall back to standalone `CurlReadOp`/`CurlPgReadOp`, and reject non-sequential reads in full-download mode. `Write` starts or continues a single PUT, requiring sequential offsets. `Close` finalizes a PUT, creates a zero-sized object if opened write-only with no writes, or returns immediately for read handles.

## State and Persistence
Persistent remote state is changed by PUT and close-created zero-length objects. In-memory state tracks open flag, full-download flag, open flags, base/last/current URLs, mutable properties under shared mutex, header timeout, pending PUT/read operations, prefetch offsets and handlers, expected upload size, write offset, header callout pointer, and global prefetch counters.

## Dependencies and Integration Points
The file integrates `XrdCl` file plugin APIs, HTTP curl operation classes, response-info wrappers, timeout parsing, worker maintenance settings, XrdCl logging/env constants, CRC utilities, page size, JSON output, and header/connection callout mechanisms.

## Risks and Test Signals
Important risks include raw handler lifetimes, callbacks that may delete the `File`, sequential-only assumptions for full download and PUT, dynamic URL cache invalidation, disabled prefetch after short reads, and the moved-buffer constructor path where size accounting must remain correct. Tests should cover open flag combinations, 404 open-for-create, timeout parsing bounds, full-download sequential read EOF, prefetch continuation/failure resubmission, PUT queueing/final flush/partial-size close, dynamic query replacement, Fcntl XAttr JSON, page checksum correctness, and destructor waiting for active writes.
