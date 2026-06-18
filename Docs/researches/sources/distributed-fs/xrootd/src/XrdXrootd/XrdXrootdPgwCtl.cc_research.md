# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwCtl.cc

Purpose: implements pgwrite control framing: it maps client checksum+data stream layout into iovec frames that can be read from the socket and verified/written in bounded chunks.

Important APIs/types/functions: constructor preinitializes response status and iovec checksum/data slots. `Setup()` computes total layout for a pgwrite request using `XrdOucPgrwUtils::recvLayout()`. `Advance()` moves to the next frame when the request is larger than the current buffer.

Control flow: `Setup()` clears any previous short-read iovec length, validates the requested offset/length layout, computes maximum iovec elements supported by the current `XrdBuffer`, refreshes data buffer pointers when the buffer changes, sets the first data pointer for unaligned leading data, initializes frame counters and response offset, and resets bad-checksum state. `Advance()` restores the first data slot to a full page, consumes remaining iovec entries, applies short final segment length when needed, and recomputes the socket read length for the next frame.

State and persistence behavior: state is per-control object: current buffer pointer/size, iovec counts and remaining entries, current frame length, end segment length, index needing reset, checksum vector, and response status/body. No durable storage is owned; inherited bad-checksum state may update file-level tracking during verification elsewhere.

Dependencies: `XrdOucPgrwUtils`, `XrdSysPlatform`, `XrdXrootdFile`, `XrdXrootdPgwFob`, `XrdBuffer`, protocol constants, and `XrdXrootdPgwBadCS`.

Integration points: used by pgwrite request handlers to produce `getData()` iovecs and later expose checksum vector/data pointers through `FrameInfo()` and `FrameLeft()`.

Risks: assumes caller-provided buffers are at least 4 KiB and sizes are power-of-1K; too-small buffers produce logic errors. `fixSRD` must be reset or short final-page lengths leak into later requests. `iovMax` calculation floors by page size, so non-page-sized buffers waste tail space. Layout must remain synchronized with `XrdOucPgrwUtils`.

Test signals: aligned and unaligned writes, request larger than 1 MiB, short last page, small buffer rejection, repeated reuse with different buffers, `Advance()` frame lengths, and checksum/data pointer extraction.
