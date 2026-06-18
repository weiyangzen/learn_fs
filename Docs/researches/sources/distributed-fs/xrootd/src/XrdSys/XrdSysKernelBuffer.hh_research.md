## sources/distributed-fs/xrootd/src/XrdSys/XrdSysKernelBuffer.hh

Purpose: implements a Linux-oriented zero-copy-ish kernel buffer abstraction around pipes, `splice`, and `vmsplice`.

Important APIs/types/functions: class `XrdSys::KernelBuffer`; public `Empty()` and `IsPageAligned()`; private `Alloc`, `Free`, `ReadFromFD`, `WriteToFD`, `ToUser`, and `FromUser`; free helper functions `Read(fd, buffer, length[, offset])`, `Write(fd, buffer, offset)`, `Send(fd, buffer)`, and `Move()` in both directions.

Control flow: reading frees existing pipes, allocates one or more pipes up to `MAX_PIPE_SIZE`, splices fd data into pipe write ends, and tracks per-pipe data size. Writing splices pipe read ends to an fd/socket and drains state. `ToUser()` allocates a page-aligned user buffer and vmsplices/copies pipe data into it. `FromUser()` requires page alignment, vmsplices with `SPLICE_F_GIFT`, frees the user buffer on success, and sets it null.

State and persistence: `capacity`, `size`, `pipes`, and `pipes_cursor` are object state. Pipe fds are closed in `Free()`/destructor. No durable state.

Dependencies and integration: POSIX `pipe`, `fcntl`, `splice`, `vmsplice`, `posix_memalign`, and vector/array/tuple. If splice support macros are missing, operations return `-ENOTSUP`.

Risks: move constructor and move assignment reset `capacity`/`size` on the destination rather than the source in the shown code, which appears to lose ownership accounting and can leak/skip cleanup. `Alloc()` leaks pipe fds if `F_SETPIPE_SZ` fails. `ToUser()` uses `delete[] buffer` on a pointer managed as `free()`/`posix_memalign`, likely wrong. State is not thread-safe.

Test signals: splice-supported and unsupported builds, read/write/send round trips, offset and non-offset paths, page-alignment rejection, `FromUser()` ownership transfer, move construction/assignment destructor behavior, and failure injection for `fcntl`, `splice`, and `posix_memalign`.
