## sources/distributed-fs/xrootd/src/Xrd/XrdPoll.hh

Purpose: declares the abstract poller interface and common state for event backends that drive active links.

Important APIs/types/functions: static APIs `Attach`, `Detach`, `Finish`, `Poll2Text`, `Setup`, and `Stats` provide backend-independent operations. Virtual APIs `Disable`, `Enable`, `Start`, `Exclude`, and `Include` are implemented by `XrdPollE` or `XrdPollPoll`. `PipeData` encodes command-pipe requests (`EnFD`, `DiFD`, `RmFD`, `Post`).

Control flow: link activation attaches `XrdPollInfo` to a backend. Backends wait for fd readiness and command-pipe requests, disable links while work is scheduled, and reenable links after protocol processing succeeds.

State/persistence: each poller stores thread identity, command/request pipe fds, pipe buffers, attached counts, and event counters. Static `Pollers` holds the active backend objects.

Dependencies/integration: depends on POSIX `pollfd`, pthreads, `XrdSysSemaphore`, and `XrdPollInfo`.

Risks: subclass correctness depends on honoring command-pipe semantics and maintaining `numEnabled`, `numEvents`, and `numInterrupts`. `XRD_NUMPOLLERS` is fixed at three; scaling changes require reviewing attachment balancing and stats sizing.

Test signals: backend conformance tests should verify include/exclude, enable/disable, pipe posts, thread startup synchronization, and stats length when called with null buffer.
