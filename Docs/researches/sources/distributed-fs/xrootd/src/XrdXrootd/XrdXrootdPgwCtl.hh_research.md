# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.hh

Purpose: declares the pgwrite control object that combines bad-checksum tracking with socket iovec layout and final response metadata.

Important APIs/types/functions: constants `crcSZ`, `maxBSize` (`1 MiB`), and `maxIOVN`; response fields `resp` and `info`; methods `Setup`, `Advance`, `FrameInfo()` overloads, and `FrameLeft()`. Internal arrays `csVec` and `ioVec` hold checksums and alternating checksum/data iovecs.

Control flow: a handler calls `Setup()` for a request, uses `FrameInfo(iovn,rdlen)` to read checksum+data from the socket, verifies/writes the frame, then calls `Advance()` until all frames are consumed. The second `FrameInfo()` exposes decoded checksum vector and contiguous data when the caller still owns the expected buffer.

State and persistence behavior: per-object transient request state, with inherited bad-checksum collection. Persistent effects are external file writes and bad-offset tracking.

Dependencies: `sys/uio.h`, `XProtocol`, `XrdBuffer`, `XrdSysPageSize`, and `XrdXrootdPgwBadCS`.

Integration points: used by synchronous pgwrite paths and related AIO helpers to avoid hand-building iovec layouts at each call site.

Risks: the overload returning checksum/data pointers validates buffer identity; callers that pass a recycled/different `XrdBuffer` get null. `FrameLeft()` arithmetic depends on the alternating iovec layout. The fixed max buffer/iovec sizing must be kept in step with protocol page size.

Test signals: `FrameInfo` null when buffer mismatches, partial-frame `FrameLeft()` lengths, max buffer layout, page-size constant changes, and response status fields for pgwrite final result.
