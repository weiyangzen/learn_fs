# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdNormAio.cc

Purpose: implements asynchronous normal read/write tasks that copy data between an `XrdSfs` file and a client link while preserving protocol response ordering and request accounting.

Important APIs/types/functions: static `Alloc()`, `Read()`, `Write()`, `DoIt()`, `Recycle()`, private read path `CopyF2L_Add2Q()`/`CopyF2L()`, write path `CopyL2F()` overloads, and `Send()`. A local free list caches up to 64 task objects.

Control flow: `Read()` initializes offsets/length/state, refs the link and file, increments protocol AIO request count, and schedules through the file AIO fob. `CopyF2L_Add2Q()` issues file `read(XrdSfsAio*)` requests until data or buffer limits are reached. `CopyF2L()` consumes completed buffers, validates results, queues out-of-order completions by offset, sends in-order chunks as `kXR_oksofar`, saves a final buffer to avoid an extra response, then sends final `kXR_ok`. `Write()` starts a socket-bound transfer; `CopyL2F()` reads data from the client into AIO buffers, issues file writes, processes completions, and sends the final response.

State and persistence behavior: per-task state inherited from `XrdXrootdAioTask` includes file/link/protocol, offsets, remaining length, in-flight count, final read, pending write, state flags, and response object. `XrdXrootdNormAio` adds send queue, next expected send offset, reorder count, and scheduling flag. Persistent effects are file reads/writes and client responses.

Dependencies: `XrdXrootdAioBuff`, `XrdXrootdAioFob`, `XrdXrootdFile`, `XrdSfsInterface`, `XrdScheduler`, `XrdLink`, `XrdXrootdResponse`, tracing, and protocol `as_maxperreq`.

Integration points: used by xrootd file read/write request handling when normal asynchronous I/O is available. It cooperates with the file AIO fob for scheduling and with the protocol for socket reads and outstanding request accounting.

Risks: read completions can arrive out of order, making the sorted send queue critical; a missing offset triggers an `ENODEV` error. Writes cannot relinquish the socket-handling thread in the same way reads can, so blocking behavior differs. Reference counts must be decremented exactly once via `aioHeld`. Link-send errors mark `aioDead` and reset pending AIO for the protocol.

Test signals: multi-buffer reads with out-of-order completion, final-response optimization, missing completion/gap error, max in-flight throttling, read link disconnect, write socket short/error returns, file read/write `SFS_OK` and error mapping, recycle free-list cap, and request/refcount accounting.
