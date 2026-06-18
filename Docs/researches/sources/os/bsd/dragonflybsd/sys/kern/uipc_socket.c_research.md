# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_socket.c

## Role

This file implements DragonFlyBSD's generic socket operations above protocol-specific `pru_*` methods and below syscall wrappers. It owns socket allocation, creation, bind/listen/connect/disconnect/accept dispatch, close and free paths, generic send/receive loops, socket options, shutdown/receive flush, accept filters, out-of-band notification, and kqueue filters.

The file is the main policy layer for `struct socket`. Protocol implementations provide behavior through `struct pr_usrreqs`; this file enforces common socket semantics, reference transitions, buffer locking, blocking behavior, and user-visible option behavior.

## Allocation, Creation, And Listen Queues

`soalloc()` allocates and initializes a socket: protocol pointer, async I/O job queue, receive/send message lists, socket-buffer tokens, receive-done netmsg, initial `SS_NOFDREF` state, reference count, and anonymous inode number.

`socreate()` resolves a protocol by domain/type/protocol, checks jail network-family restrictions, allocates the socket, assigns a protocol message port, initializes listen queues, stores type and credentials, and attaches the protocol through either `so_pru_attach_fast()` or `so_pru_attach()`. On failure it restores `SS_NOFDREF` and frees the allocation reference.

`solisten()` rejects already connected/connecting sockets, sets `SO_ACCEPTCONN` when the completed queue is empty, clamps backlog to `somaxconn`, stores `so_qlimit`, and calls the protocol listen method.

`soinherit()` moves completed accepted sockets from one listening socket to another, replacing accepted-socket credentials with the inheriting listener's credentials and waking the inheriting listener if connections moved.

## Close, Free, And Abort

`soclose()` marks `SS_ISCLOSING`, clears async ownership, and chooses synchronous or fast close. It uses synchronous close for synchronous protocols, disabled fast-close mode, and connected sockets with active linger.

`soclose_sync()` waits for pending async protocol requests to drain for asynchronous protocols, initiates disconnect when needed, honors `SO_LINGER`, detaches the protocol, then marks `SS_NOFDREF` and drops the socket reference. A protocol may return `EJUSTRETURN` to finish `sodiscard()`/`sofree()` itself.

`soclose_fast()` sends a close netmsg to the socket's protocol port. The handler disconnects and detaches through direct protocol methods, then discards and frees the socket unless the protocol takes over.

`sofree()` drops a reference and only destroys the socket when the last reference is gone, the protocol control block is gone, and `SS_NOFDREF` is set. It interlocks with accept queues using the listen socket's pool token. A completed queued socket is deliberately not decommissioned because `accept(2)` may have been signaled already.

`soqflush()` aborts all incomplete and complete children of a listening socket. `soabort_async()` and `soabort_direct()` take a reference before dispatching protocol abort so socket close cannot race the protocol path.

## Connect And Accept

`soaccept_generic()` converts a referenced socket from `SS_NOFDREF` ownership into descriptor ownership. `soaccept()` then calls the protocol accept method.

`soconnect()` rejects listen sockets, enforces single-connect behavior for connection-required protocols, supports disconnect/reconnect behavior for connectionless protocols, clears stale `so_error`, and dispatches connect synchronously or asynchronously depending on protocol fast-path support.

`soconnect2()` delegates socket-pair linkage to the protocol. `sodisconnect()` validates connected/not-already-disconnecting state before calling the protocol disconnect method.

## Send Paths

`sosend()` is the generic send loop. It validates `MSG_EOR` use, handles `MSG_DONTROUTE`, locks the send buffer, enforces connected and buffer-space rules, blocks through `ssb_wait()` when needed, builds mbuf chains from `uio`, marks `M_EOR` when requested, chooses protocol send flags such as `PRUS_OOB`, `PRUS_EOF`, and `PRUS_MORETOCOME`, calls `so_pru_send()`, and frees unsent data/control on exit. It also maps `EPIPE` to SIGPIPE behavior at the syscall layer.

Under `INET`, `sosendudp()` specializes the generic path for UDP assumptions: atomic datagrams, no control data, no out-of-band data, and optional async `so_pru_send_async()`. It can allocate headroom for protocol/link headers when `udp_sosend_prepend` is enabled.

Also under `INET`, `sosendtcp()` specializes for TCP. It rejects `MSG_EOR`, rejects non-empty control data, uses preallocation accounting through `ssb_space_prealloc()` and `ssb_preallocstream()`, can allocate jumbo clusters, batches up to `tcp_sosend_agglim`, and dispatches async sends except for OOB or `MSG_SYNC`.

## Receive Paths

`soreceive()` is the generic receive loop. It supports OOB reads, address and control extraction, `MSG_PEEK`, `MSG_WAITALL`, atomic-record truncation, `MSG_EOR`, receive low-water blocking, receive errors, EOF, and optional return of data into another sockbuf. It externalizes `SCM_RIGHTS` control data through the protocol domain's `dom_externalize` hook and disposes rights if the caller did not request control data.

The implementation depends on the record layout produced by `sbappend*()`:

- optional address mbuf first for protocols with `PR_ADDR`
- zero or more `MT_CONTROL` mbufs
- data mbufs

`sorecvtcp()` is the TCP-specific receive path. It locks a bounded run of receive mbufs with `M_SOLOCKED`, releases the receive token for user copyout, then reacquires the token to unlink or trim the consumed bytes. This reduces protocol-thread blockage while avoiding `sbcompress()` coalescing into mbufs being copied.

Both receive paths call `so_pru_rcvd()` or `so_pru_rcvd_async()` when data is drained so protocols can reopen receive windows or send acknowledgements.

## Shutdown, Flush, And Ancillary Disposal

`soshutdown()` validates `SHUT_RD`, `SHUT_WR`, and `SHUT_RDWR`. Read shutdown flushes the receive side through `sorflush()`; write shutdown calls the protocol shutdown method.

`sorflush()` marks the receive buffer no-interrupt, takes the receive token, sets `SS_CANTRCVMORE`, snapshots the old buffer, clears live buffer fields while preserving the containing `signalsockbuf`, disposes rights through `dom_dispose` when required, and releases queued mbufs and reserved receive space.

## Socket Options

`sosetopt()` handles `SOL_SOCKET` options and delegates non-socket-level options to protocol `pr_ctloutput`.

Supported set options include:

- `SO_ACCEPTFILTER` when `INET` is enabled.
- `SO_LINGER`.
- Boolean options such as `SO_DEBUG`, `SO_KEEPALIVE`, `SO_DONTROUTE`, `SO_BROADCAST`, `SO_REUSEADDR`, `SO_REUSEPORT`, `SO_OOBINLINE`, `SO_TIMESTAMP`, `SO_NOSIGPIPE`, `SO_RERROR`, and `SO_PASSCRED`.
- Buffer sizes and low-water marks.
- send/receive timeouts.
- `SO_USER_COOKIE`.

`sogetopt()` returns corresponding values plus `SO_TYPE`, `SO_ERROR`, `SO_SNDSPACE`, `SO_CPUHINT`, and accept-filter state. `SO_ERROR` consumes pending send or receive error state.

The helper families `soopt_to_kbuf()`/`soopt_from_kbuf()` and `soopt_to_mbuf()`/`soopt_from_mbuf()` support kernel-buffer and mbuf-backed protocol options.

## Accept Filters

When `INET` is enabled, `do_setopt_accept_filter()` installs or removes accept filters on listening sockets only. It looks up filter implementations by name, runs optional create/destroy callbacks, stores filter argument state, and toggles `SO_ACCEPTFILTER`.

Connections completing under an accept filter are kept out of the completed queue until the filter callback promotes them.

## Kqueue And Notification

`sokqfilter()` attaches read, write, exception, or listen filters to the appropriate socket buffer knote list and sets `SSB_KNOTE`.

`filt_soread()` reports receive availability, EOF, HUP, OOB-at-mark state, pending errors, low-water behavior, and listen-queue readiness. It is careful not to emit spurious HUP-only poll events.

`filt_sowrite()` reports send space, EOF/HUP, pending send errors, connection-required readiness, and low-water behavior.

`filt_solisten()` reports completed-connection count, capped by `soavailconn` when configured.

`sohasoutofband()` sends SIGURG and notifies receive knotes without using `NOTE_OOB` as a hint.

## Tunables And Diagnostics

The file defines `M_SOCKET`, `M_SONAME`, and `M_PCB` malloc types and exposes sysctls for `somaxconn`, fast close, fast accept predication, async sendfile, async connect, fast create, and maximum reported available listen connections.

## Notable Assumptions And Risks

- Socket lifetime is split between descriptor ownership (`SS_NOFDREF` clear), protocol PCB ownership, accept queue membership, and explicit references. Many paths rely on exact state transitions.
- Some fast paths run on protocol message ports and use direct protocol calls only when already on the right port or for synchronous protocols.
- Comments identify stale-state races around send-side checks after blocking `uiomove()` or page faults; the code mitigates by rechecking in several paths but keeps historical XXX notes.
- `sorecvtcp()` relies on `M_SOLOCKED` and `sbcompress()` respecting it.
- `sorflush()` intentionally clears only buffer subfields, not the whole `signalsockbuf`, because tokens, knotes, and other container state must survive.
