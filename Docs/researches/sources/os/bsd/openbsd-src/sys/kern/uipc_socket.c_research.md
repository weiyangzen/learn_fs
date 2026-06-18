# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_socket.c

Generic kernel socket operations.

This file provides socket allocation, lifecycle, send/receive, option handling, kqueue filters, and optional socket splicing. `soinit()` initializes the socket pool. `soalloc()` zero-allocates a socket, initializes reference counts, socket locks, receive/send sockbuf locks and mutexes, kqueues, async I/O state, and listen queues. `socreate()` finds the protocol switch, allocates a socket, records creator credentials, attaches protocol state, and returns a live socket.

Connection setup and teardown wrap protocol user requests. `solisten()` validates stream/seqpacket sockets, calls `pru_listen()`, clamps backlog between `sominconn` and `somaxconn`, and marks accept sockets. `sofree()`, `sorele()`, and `soclose()` coordinate reference release, protocol detach, lingering close, accept-queue cleanup, async I/O revocation, socket-buffer release, rights disposal, and final pool return. `soaccept()`, `soconnect()`, `soconnect2()`, `sodisconnect()`, `soabort()`, `soshutdown()`, and `sorflush()` expose protocol-facing accept/connect/disconnect/shutdown semantics.

`sosend()` serializes writers with the send sockbuf lock, validates connection state, handles nonblocking/atomic send buffer limits, reserves space for control data, copies userspace data into mbufs via `m_getuio()`, marks end-of-record and zeroization, and dispatches to `pru_send()` or `pru_sendoob()`. It handles short writes on interrupt/would-block through its callers and raises `EPIPE` for closed send sides.

`soreceive()` is the main receive path. It handles out-of-band reads, blocking and `MSG_WAITALL`, address records, control records, `SCM_RIGHTS` externalization/disposal through domain hooks, `MSG_PEEK`, atomic-message truncation, out-of-band marks, copying to user buffers or returning mbuf chains, and `PR_WANTRCVD` callbacks. The helper `sbsync()` keeps socket-buffer record pointers coherent while data is removed and locks are temporarily dropped for `uiomove()`.

When compiled with `SOCKET_SPLICE`, `sosplice()`, `sounsplice()`, `soidle()`, `sotask()`, and `somove()` connect a source receive buffer to a drain send buffer for TCP-style zero-copy movement. The splice path validates protocol compatibility, max byte limits, idle timeouts, socket state, and loop counters; moves data mbufs between buffers; handles urgent data; triggers window updates; and unsplices on EOF, errors, max length, or timeout.

`sosetopt()` and `sogetopt()` implement `SOL_SOCKET` options including linger, boolean options, buffer sizes and low water marks, timeouts, routing table delegation, splice controls, and UNIX peer credentials. Non-socket-level options are delegated to protocol `pr_ctloutput()`. `soo_kqfilter()` and the filter callbacks implement read/write/exception readiness, low-water support, EOF/error reporting, accept-queue readiness, poll/select hangup behavior, and OOB notification. DDB helpers print socket and sockbuf state.

Notable constraints: INET/INET6 sockets use the global network lock while other domains use per-socket locks; receive code relies on the exact record layout created by `sbappend*()`; socket splicing is conditional and protocol-limited; and many close/free paths must preserve accept-queue semantics to avoid races after readiness notification.
