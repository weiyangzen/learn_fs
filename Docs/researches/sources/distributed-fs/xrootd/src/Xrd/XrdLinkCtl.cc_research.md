## sources/distributed-fs/xrootd/src/Xrd/XrdLinkCtl.cc

Purpose: manages the global fd-indexed table of reusable link objects, allocates links for accepted sockets, scans active links, schedules idle timeouts, and reconciles aggregate link statistics.

Important APIs/types/functions: `Alloc()` validates the accepted fd, lazily allocates blocks of `XrdLinkCtl` objects, assigns a monotonically increasing `Instance`, initializes host/client identity, fd state, read-lock/non-close options, and link counters. `Find()` and `getName()` iterate active table slots with optional `XrdLinkMatch`. `idleScan()` disables idle enabled links. `Setup()` creates `LinkTab`/`LinkBat` and schedules `LinkScan`. `Unhook()` marks an fd free. `RegisterCloseRequestCb()` forwards callback registration to `XrdLinkXeq`.

Control flow: configuration calls `Setup(maxfds, idlewait)`. The network layer accepts a socket and calls `Alloc(peer, opts)`. Polling uses `LinkTab`/`LinkBat` for fd lookup and close paths call `Unhook()` before fd close. If idle scanning is configured, `LinkScan::DoIt()` repeatedly schedules itself through `XrdScheduler`.

State/persistence: maintains process-global `LinkTab`, `LinkBat`, `LTLast`, `maxFD`, `myInstance`, kill wait constants, and idle scan intervals. Link objects are never freed during normal operation; slots are marked free for reuse.

Dependencies/integration: integrates with `XrdInet` for hostname trimming, `XrdScheduler` for idle scan jobs, `XrdPoll` for disabling timed-out links, `XrdLinkXeq` statistics, and global logging/tracing.

Risks: fd table size must match configured connection limits; out-of-range or reused fds are rejected. `Find()` increments a link reference after releasing `LTMutex` and validates `Instance`, which is the main protection against fd reuse races. `idleScan()` increments a signed `char isIdle`; long intervals or unexpected overflow would affect idle detection.

Test signals: test fd allocation/reuse, table block allocation boundaries, instance mismatch during concurrent close/find, idle timeout disabling, `XRDLINK_RDLOCK` and `XRDLINK_NOCLOSE` options, and `LTLast` shrink after unhooking the highest fd.
