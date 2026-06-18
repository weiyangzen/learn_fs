# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioPgrw.cc

Purpose: implements the page-read/page-write AIO buffer variant. It extends the base AIO buffer with checksum slots and an interleaved `iovec` layout for xrootd page data, where each page has a checksum followed by page bytes.

Important APIs and functions: the constructor lays out `ioVec` as alternating checksum and page entries, reserves `ioVec[0]` as a network-leading element, initializes `cksVec`, and labels the AIO object. `Alloc()` caches whole page AIO objects and keeps their larger `aioSZ` buffers instead of returning buffers on every recycle. `Setup2Recv()` and `Setup2Send()` call `XrdOucPgrwUtils::{recvLayout,sendLayout}` to validate offsets and lengths, set first/last segment lengths, choose the data pointer into the backing buffer, and fill `sfsAio`. `iov4Recv()`, `iov4Send()`, and `iov4Data()` expose correctly sized vectors; `iov4Send()` can convert checksums to network order.

Control flow and state: `csNum` is the active checksum/page count, and `iovReset` remembers a shortened last page segment that must be restored before reuse. `Recycle()` returns the full object to a smaller static free list (`maxKeep` 64) and intentionally retains the buffer to avoid churn for page I/O.

Dependencies and integration: uses `XrdOucPgrwUtils`, protocol page constants, `XrdXrootdPgrwAio::aioSZ`, global `BPool`, and file stats/tracing infrastructure. It is allocated by page-read/write task code and completed through the base `XrdSfsAio` callbacks.

Risks and test signals: off-by-one errors in `ioVec` indexing can corrupt checksum/data framing. Important tests include unaligned offsets, partial first and last pages, full 16-page segments, checksum byte-order conversion, no-checksum fallback via `noChkSums()`, and reuse after a truncated segment.
