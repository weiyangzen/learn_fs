# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_socket.c

This file is the FreeBSD kernel socket layer core. It owns socket allocation and lifetime, listen queues, generic send/receive implementations, socket options, socket readiness notification, state transition helpers, and the `SO_SPLICE` in-kernel socket-to-socket data path.

Key entry points:
- `socreate()` allocates a socket, selects a protocol switch entry, enforces Capsicum and jail address-family policy, initializes credentials/FIB/MAC labels/knote lists, and calls protocol attach.
- `soclose()`, `soabort()`, `sorele_locked()`, `sofree()`, and `sodealloc()` implement the close, abort, reference-release, protocol-detach, sockbuf-destroy, knote-drain, MAC cleanup, and UMA-free lifecycle.
- `solisten()`, `solisten_proto_check()`, `solisten_proto()`, `solisten_clone()`, `sonewconn()`, `solisten_enqueue()`, `solisten_dequeue()`, and `solisten_wakeup()` implement the passive-open/listen socket state machine and accept queues.
- `sobind()`, `sobindat()`, `soconnect()`, `soconnectat()`, `soconnect2()`, `sodisconnect()`, `soaccept()`, `sosockaddr()`, and `sopeeraddr()` are protocol-dispatch wrappers around bind/connect/disconnect/address operations.
- `sosend_dgram()`, `sosend_generic()`, `sosend_generic_locked()`, `sosend()`, and `sousrsend()` implement datagram and generic send behavior, including control mbufs, routing flags, KTLS framing, blocking rules, partial-progress handling, and SIGPIPE policy.
- `soreceive_generic()`, `soreceive_generic_locked()`, `soreceive_stream()`, `soreceive_stream_locked()`, `soreceive_dgram()`, `soreceive_rcvoob()`, and `soreceive()` implement generic, optimized stream, optimized datagram, and out-of-band receive paths.
- `sosetopt()`, `sogetopt()`, `sooptcopyin()`, `sooptcopyout()`, `soopt_getm()`, `soopt_mcopyin()`, `soopt_mcopyout()`, and `so_setsockopt()` implement `SOL_SOCKET` option handling and shared protocol option-copy helpers.
- `sopoll_generic()`, `sokqfilter_generic()`, `filt_soread()`, `filt_sowrite()`, and `filt_soempty()` expose readiness to `poll(2)` and kqueue.
- `soisconnecting()`, `soisconnected()`, `soisdisconnecting()`, and `soisdisconnected()` are protocol-called state transition helpers that perform wakeups and listen-queue promotion.
- `soshutdown()`, `sorflush()`, `sosetfib()`, `sohasoutofband()`, `socheckuid()`, `soupcall_set()`, `soupcall_clear()`, `solisten_upcall_set()`, `sodupsockaddr()`, `sodtor_set()`, and `sotoxsocket()` provide miscellaneous socket-layer services.

Core mechanics:
- Socket objects come from the `socket` UMA zone. `soalloc()` initializes locks, socket buffers, AIO task hooks, VNET ownership, MAC state, helper OSD, generation counters, and open-socket accounting. `sodealloc()` reverses socket-layer setup after protocol state has already been detached.
- `so_global_mtx` protects `so_gencnt`, `numopensockets`, and per-socket generation count updates. VIMAGE builds also maintain per-VNET socket counts.
- Socket-buffer ownership is split between protocol-managed buffers marked `PR_SOCKBUF` and generic socket-layer buffers. `soattach()` bridges the two models and reserves accepted sockets from listener buffer limits.
- Listen sockets are structurally different from ordinary sockets: `solisten_proto()` destroys generic send/receive buffers, preserves buffer limit/low-water/time-out settings in `sol_*` fields, initializes incomplete/complete queues, and sets `SO_ACCEPTCONN`.
- Listen queue overflow is rate-limited and logged with socket description data for INET/INET6/UNIX listeners. `kern.ipc.soacceptqueue` and hidden compatibility `kern.ipc.somaxconn` share the same backing tunable.
- Accept queue entries hold references to the listening socket. `solisten_dequeue()` transfers the queued child socket reference to the caller, optionally inheriting nonblocking state, while `soclose()` drains both complete and incomplete queues and aborts children outside the listener lock.
- Accepted and cloned sockets inherit only selected listener options such as keepalive, linger, OOB-inline, no-SIGPIPE, and accept-filter state. The comments explicitly warn that broad option inheritance is historical compatibility, not an application contract.
- `soisconnected()` promotes sockets from the incomplete queue to the complete queue, including accept-filter callback handling. It uses careful lock retrying because promotion needs both child and listener state.
- `sosend_generic_locked()` serializes senders with the socket I/O send lock, checks connection state and send-buffer space, handles `MSG_DONTROUTE`, `MSG_EOF`, `MSG_MORETOCOME`, `MSG_EOR`, and KTLS record typing, copies user data to mbufs when needed, and calls `pr_send()`.
- `soreceive_generic_locked()` serializes readers with the socket I/O receive lock, maintains socket-buffer record invariants while dropping the sockbuf mutex for `uiomove()`, handles source addresses, control data, `MSG_PEEK`, `MSG_WAITALL`, OOB data, record truncation, and `PR_WANTRCVD` notifications.
- `soreceive_stream_locked()` is a faster stream path for simple TCP-like receive cases. It bypasses record/control handling but falls back to the generic receiver when KTLS receive framing is present.
- `soreceive_dgram()` is a fast userspace datagram path. It removes one datagram atomically from the receive queue, copies address/control/data out, and can drop the datagram on copyout failure because datagrams are atomic.
- KTLS is integrated in both send and receive paths. Send may frame mbufs and enqueue software TLS work; receive falls back to generic control-message-aware logic when TLS metadata is present.
- Socket options at `SOL_SOCKET` update flags, linger, buffer sizes, low-water marks, timeouts, FIB selection, MAC labels, timestamp clock choice, max pacing rate, listen queue metrics, and splice state. Non-`SOL_SOCKET` options are delegated to `pr_ctloutput()`.
- `sopoll_generic()` and kqueue filters suppress normal read/write readiness for sockets participating in `SO_SPLICE`, since splice owns the affected receive/send direction.
- `sotoxsocket()` exports a stable `xsocket` view for monitoring interfaces, including queue sizes, buffer snapshots, owner UID, FIB, protocol/family, and splice peer pointer when applicable.

`SO_SPLICE` behavior:
- `splice_init()` lazily creates a splice UMA zone and per-CPU worker queues/kthreads, with tunables under `kern.ipc.splice`.
- `so_splice()` currently permits only TCP-to-TCP sockets in the same VNET, rejects listening/unconnected/already-spliced sockets, rejects KTLS buffers, marks source receive and destination send buffers as spliced, and starts transfer immediately.
- Worker threads process `struct so_splice` items, set the source socket VNET, lock the source receive and destination send I/O locks with deadlock-avoidance retrying, receive available bytes from the source, and send mbufs into the destination.
- `so_splice_xfer()` updates the source socket’s transmitted byte counter while both socket I/O locks are held, requeues work if more source data and destination space exist, and automatically unsplices on errors or maximum-byte completion.
- `so_unsplice()` clears splice flags and back-pointers first to stop new work, waits for queued/running workers to close, cancels timeout tasks, wakes userspace, releases held socket references, and frees the splice structure.
- `getsockopt(SO_SPLICE)` serializes with the receive I/O lock before returning bytes transferred, intentionally making tests and user observations see up-to-date counters after observed delivery.

Important invariants:
- `pr_attach()` is called at most once after `soalloc()` and `pr_detach()` is called exactly once only if attach succeeded.
- `sofree()` requires zero socket references, no listen-queue membership for non-listeners, no active splice flags or splice back-pointers, and protocol state detachable without socket locks held.
- Protocol entry points that require VNET context are wrapped with `CURVNET_SET()` or asserted with `VNET_SO_ASSERT()`.
- Socket I/O locks serialize concurrent user senders/receivers separately from lower-level sockbuf mutexes. Some paths deliberately drop sockbuf mutexes around copyin/copyout while preserving record pointers.
- Listen queue manipulation uses explicit queue-state fields (`SQ_NONE`, `SQ_INCOMP`, `SQ_COMP`) and references to avoid freeing sockets still visible to protocol/listener paths.
- `soreceive_generic()` must keep `sb_mb`, `sb_mbtail`, `sb_lastrecord`, and `m_nextpkt` consistent even while copying to userspace or consuming address/control mbufs.
- `soisdisconnected()` uses a release fence so lockless readers do not observe all connection-state bits cleared transiently.
- For protocol-managed sockbufs (`PR_SOCKBUF`), this file does not destroy or initialize generic buffer mutex state; the protocol owns that storage discipline.

Filesystem/OS relevance:
- Although this is not a filesystem implementation, it is a core FreeBSD kernel object/lifetime and file-descriptor endpoint layer. It interacts with `struct file`, credentials, Capsicum capability rights, MAC labels, jail policy, VNETs, kqueue/poll, AIO, KTLS, and protocol control blocks. In the broader OS/VFS subset, it is important because sockets are first-class descriptor objects with close, readiness, credential, capability, and copyin/copyout behavior parallel to file-backed descriptors.

Notable risks and edge cases:
- Socket close and accept paths are reference-count delicate; queued accept children can be seen by protocol code while listener close is draining queues.
- Send and receive code intentionally contains comments about races where state checked before copyin/copyout may be stale by the time protocol send/receive callbacks run.
- `SO_SPLICE` can form loops; worker thread priorities are lowered to reduce starvation risk.
- Splice setup has multi-object rollback paths where source and destination flags, references, and timeout tasks must remain balanced.
- Datagram receive can discard a datagram if copyout fails after it has been removed from the socket buffer.
- Option handling mixes socket-layer state updates with protocol `pr_ctloutput()` callbacks; protocols may observe or further validate socket-level option changes.
