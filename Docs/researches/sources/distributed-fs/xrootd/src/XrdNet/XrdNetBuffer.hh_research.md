## sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.hh

Purpose: Declares `XrdNetBufferQ` and `XrdNetBuffer`, a small pooled buffer API for network datagrams.

Important APIs and types: `XrdNetBufferQ::Alloc`, `BuffSize`, `Recycle`, and `Set` manage queue behavior. `XrdNetBuffer` exposes public `data`, `dlen`, `BuffSize`, and `Recycle`.

Control flow: The header defines friend access so the queue can manipulate a buffer's private link and back-pointer; callers recycle through the buffer or queue.

State and persistence: Queue state is public for historical access and includes mutex, stack, size, alignment, and count fields. Buffer state is transient heap memory only.

Dependencies and integration points: Includes `XrdOucChain.hh` and `XrdSysPthread.hh`. Used by `XrdNet` UDP receive and likely legacy peer consumers.

Risks: Public mutable queue members allow callers to bypass locking. Buffer ownership is manual; using `Recycle` after the queue is destroyed would dereference a stale back-pointer. `data` is public and may be written past `BuffSize` by callers.

Test signals: Compile legacy callers that access public fields; run sanitizer tests around recycle-after-destroy, double recycle, and oversized writes in consumers.
