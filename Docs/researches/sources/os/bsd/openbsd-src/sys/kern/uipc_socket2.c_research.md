# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_socket2.c

Socket state, locking, and sockbuf primitives.

This file contains lower-level helpers for sockets and socket buffers. The state-transition routines `soisconnecting()`, `soisconnected()`, `soisdisconnecting()`, and `soisdisconnected()` update connection flags, set send/receive shutdown bits, move accepted sockets from incomplete to complete listen queues, and wake readers, writers, and accept waiters. `sonewconn()` creates child sockets for listeners, enforces low-memory/backlog limits, inherits credentials/options/watermarks/sigio, attaches protocol state, and queues the child.

Queue helpers `soqinsque()` and `soqremque()` maintain `so_q0` and `so_q` membership. `socantsendmore()` and `socantrcvmore()` set half-close state and wake the corresponding side. The lock functions encode OpenBSD's mixed locking model: INET/INET6 use the net lock, other domains use per-socket rwlocks, pair locking orders sockets by address, and assertion/sleep helpers adapt to the selected model.

Sockbuf synchronization starts with `sbwait()`, `sblock()`, `sbunlock()`, and `sowakeup()`, which provide interruptible/noninterruptible buffer serialization, wait flags, kqueue notification, wakeups, and SIGIO delivery. `soreserve()` and `sbreserve()` set high-water, low-water, and mbuf-space limits, while `sbchecklowmem()` and `sbcheckreserve()` throttle enlarged reserves under mbuf memory pressure.

The append/compress/drop layer maintains the receive/send buffer as records linked by `m_nextpkt` and mbuf chains linked by `m_next`. `sbappend()`, `sbappendstream()`, `sbappendrecord()`, `sbappendaddr()`, and `sbappendcontrol()` append stream data, record-oriented data, sender addresses, and ancillary control data. `sbcompress()` drops zero-length mbufs where possible and coalesces small writable mbufs into the previous mbuf. `sbflush()`, `sbdrop()`, and `sbdroprecord()` remove data while updating byte counts, data counts, and record tail pointers.

`sbcreatecontrol()` allocates and formats a `cmsghdr` mbuf for ancillary data. SOCKBUF_DEBUG helpers validate last-record and last-mbuf invariants.

Notable constraints: callers must hold the appropriate sockbuf mutex for append/drop functions; `sbappendaddr()` requires packet-header data mbufs when data is supplied; and buffer accounting distinguishes total bytes from data bytes so address/control records do not count as payload.
