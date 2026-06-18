## sources/distributed-fs/xrootd/src/Xrd/XrdPollE.hh

Purpose: declares the Linux epoll-backed `XrdPoll` implementation.

Important APIs/types/functions: public overrides `Disable`, `Enable`, and `Start` implement event masking and poller thread execution. Protected `Exclude` and `Include` manipulate epoll membership. Private helpers `AddWaitFd`, `HandleWaitFd`, `remFD`, and `Wait4Poller` coordinate fd removal and poll-loop quiescence. `x2Text()` formats epoll event flags.

Control flow: `XrdPoll::newPoller()` constructs `XrdPollE` with an epoll event table, epoll descriptor, and wait fd. `Start()` runs the event loop. Enable/disable and include/exclude are invoked by common link and poll control paths.

State/persistence: stores epoll event table, epoll descriptor, table capacity, wait fd, and two semaphores used to prove an `epoll_wait` loop has completed before link reset can reuse `XrdPollInfo`.

Dependencies/integration: Linux-only `<sys/epoll.h>`, common `XrdPoll`, and `XrdPollInfo`.

Risks: the header explicitly documents a use-after-reset protection mechanism around `WaitFdSem`/`WaitFdSem2`; backend changes must preserve it. `EPOLLONESHOT` support is conditional, so behavior differs by platform headers.

Test signals: Linux integration tests should cover add/remove while events are pending, disable reason propagation, one-shot reenable, hangup/error events, and wait-fd synchronization during close.
