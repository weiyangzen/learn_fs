# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgrwAio.hh

Purpose: declares the asynchronous page read/write task type for pgread/pgwrite protocol operations.

Important APIs/types/functions: `Alloc`, `DoIt`, `Read`, `Write`, `Recycle`, `aioSZ` (`64 KiB`), private `CopyF2L`, `CopyL2F`, `SendData`, `SendDone`, `VerCks`, and `badCSP`.

Control flow: overrides the common AIO task hooks while specializing buffers, protocol response framing, and checksum handling for page-granular I/O.

State and persistence behavior: task objects are pooled; request state is reset through base `Init()` plus `badCSP`. Durable effects occur through file `pgWrite()` and bad-checksum tracking.

Dependencies: `XrdXrootdAioTask`, forward declarations for `XrdXrootdAioPgrw` and `XrdXrootdPgwBadCS`.

Integration points: selected by protocol code for page-based I/O and used with `XrdXrootdPgwCtl`/`XrdXrootdPgwBadCS` in write paths.

Risks: factory ownership and lifetime of `badCSP` are external. Any mismatch between `aioSZ`, page size, and `XrdXrootdAioPgrw` layout can break framing.

Test signals: factory with and without bad-checksum recorder, state reset across pooled tasks, page-size boundary ranges, virtual callback dispatch, and final response payload generation.
