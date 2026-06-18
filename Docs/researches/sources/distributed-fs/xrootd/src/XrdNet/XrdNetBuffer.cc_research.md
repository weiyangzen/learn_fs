## sources/distributed-fs/xrootd/src/XrdNet/XrdNetBuffer.cc

Purpose: Implements aligned reusable network buffers and a locked freelist queue used mainly by UDP receive handling.

Important APIs and functions: `XrdNetBufferQ` constructor/destructor, `Alloc`, `Recycle`, `Set`, and `XrdNetBuffer` constructor are implemented.

Control flow: `Alloc` locks the queue, pops a recycled buffer if available, otherwise creates a new `XrdNetBuffer` and allocates aligned data with `posix_memalign`, then unlocks. `Recycle` deletes buffers when the freelist is at capacity or resets `dlen` and pushes the buffer back. Destructor drains the freelist.

State and persistence: Queue state includes buffer size, alignment, maximum retained buffers, current retained count, mutex, and stack. Each buffer owns an allocated `data` pointer and a back-pointer to its queue. No persistent state.

Dependencies and integration points: Uses `XrdOucStack`, `XrdOucQSItem`, `XrdSysMutex`, `sysconf(_SC_PAGESIZE)`, and `posix_memalign`. `XrdNet` UDP accept attaches these buffers to legacy peers.

Risks: `maxbuff` checks occur before locking in `Recycle`, allowing small races in retained count decisions. `Alloc` decrements `numbuff` when popping under lock, but allocation is also under lock and may block other users. `posix_memalign` is POSIX-specific; Windows support depends on platform abstraction elsewhere.

Test signals: Allocate/recycle under concurrency; verify alignment, size, maximum retained count, deletion beyond cap, destructor cleanup, and UDP datagram buffer lifetime through `XrdNetPeer`.
