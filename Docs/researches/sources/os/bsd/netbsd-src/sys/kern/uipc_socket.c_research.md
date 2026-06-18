# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_socket.c

This file is the syscall-facing socket operation layer. It creates sockets and file descriptors, drives protocol user-request methods, implements close/abort/accept/connect/disconnect/send/receive/shutdown, manages SOL_SOCKET options, exposes kqueue/poll readiness, supports timestamp control messages, and provides socket sysctls.

Initialization is split: `soinit()` creates socket sysctls, initializes zero-copy loan state, allocates `softnet_lock`, initializes CVs, calls `soinit2()` from `uipc_socket2.c`, sets `sb_max`, and registers a kauth network listener. `soinit1()` starts the `sopendfree` kthread used to release loaned pages outside interrupt context. The kauth listener permits common socket opens/binds and limits connection dropping to owners unless a security model overrides.

Zero-copy send support uses `sosend_loan()` to loan user pages into kernel virtual address space for large sends when enabled. It reserves KVA against `somaxkva`, loans pages with UVM, maps them read-only into kernel space, attaches them as `M_EXT_PAGES|M_EXT_ROMAP`, and advances the `uio`. `soloanfree()` queues deferred unloan/free work to `sopendfree_thread()`.

Socket lifecycle APIs include `socreate()`, `fsocreate()`, `sobind()`, `solisten()`, `sofree()`, `soclose()`, `soabort()`, `soaccept()`, `soconnect()`, `soconnect2()`, and `sodisconnect()`. They coordinate protocol attach/detach, lock sharing, accept queues, linger behavior, credential ownership, uid socket-buffer accounting, and `SS_NOFDREF` lifetime transitions.

`sosend()` serializes writers with `sblock`, checks connection/error/shutdown state, enforces atomic message and control-buffer sizing, waits for send space, builds mbuf chains from either `uio` or caller-provided mbufs, optionally loans pages, copies data otherwise, handles `MSG_EOR`, `MSG_OOB`, `MSG_DONTROUTE`, `SS_MORETOCOME`, and calls protocol `pr_send`/`pr_sendoob`.

`soreceive()` serializes readers and preserves sockbuf invariants while dropping locks for `uiomove`. It handles OOB reads, blocking/low-water/`MSG_WAITALL` rules, optional sender address extraction, optional SCTP address behavior, control mbuf externalization/disposal (`SCM_RIGHTS`), peeking, returning mbuf chains directly, truncation of atomic records, OOB marks, protocol `pr_rcvd`, and restart-on-fd-close semantics.

Options are handled by `sosetopt1()`/`sogetopt1()` for SOL_SOCKET and delegated to protocol `pr_ctloutput` otherwise. Supported local options include linger, boolean flags, buffer sizes/low water marks, timeouts, accept filters, error retrieval, and overflow counts. `sockopt_*` helpers manage inline versus allocated option storage and legacy mbuf conversion.

Readiness support includes out-of-band notification, kqueue filters for read/listen/write/empty, and poll readiness with a fast unlocked path outside DIAGNOSTIC builds. Sysctls manage `kern.somaxkva`, `kern.sofixedbuf`, `kern.sbmax`, and default `kern.sooptions`.

Primary risks are concurrency and state-machine correctness: socket locks can change, send/receive drop locks around user copies, socket buffer pointers must remain synchronized with concurrent protocol appends, SCM_RIGHTS must be disposed/externalized exactly once, linger/close must not orphan queued sockets, and zero-copy page loans must always release KVA and UVM loans.
