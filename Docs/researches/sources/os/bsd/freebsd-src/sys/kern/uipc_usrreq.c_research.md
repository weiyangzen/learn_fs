# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_usrreq.c

## Role

Implements FreeBSD `AF_LOCAL` / Unix-domain sockets for `SOCK_STREAM`, `SOCK_DGRAM`, and `SOCK_SEQPACKET`. It is a kernel IPC transport, but it is tightly coupled to VFS because pathname-bound Unix sockets are represented as `VSOCK` vnodes and because descriptor passing can recursively carry sockets through socket buffers.

## Main Responsibilities

- Registers the local domain protocol family through three `protosw` instances and `DOMAIN_SET(local)`.
- Allocates and tracks `struct unpcb` protocol control blocks for local sockets.
- Implements bind/connect/listen/accept/disconnect/shutdown/sense/address operations.
- Implements custom send/receive paths for stream, datagram, and seqpacket Unix sockets.
- Handles ancillary data, especially `SCM_RIGHTS`, credentials, timestamps, and persistent local credentials.
- Runs garbage collection for cycles caused by file descriptors passed over Unix sockets.
- Coordinates VFS socket-vnode binding, connection lookup, and vnode reclamation.

## Important Data Structures

- `struct unpcb`: per-socket Unix-domain PCB stored in `so->so_pcb`.
- `unp_shead`, `unp_dhead`, `unp_sphead`: global PCB lists by socket type.
- `unp_link_rwlock`: protects global PCB lists, generation count, and GC state.
- `unp_defers_lock`: protects deferred file-close list and also backs `UNP_REF_LIST_LOCK`.
- `unp_vp_mtxpool`: serializes VSOCK vnode association changes.
- `unp_gc_task`: async GC task for socket/reference cycles.
- `unp_defer_task`: async close task for recursively nested `SCM_RIGHTS` file/socket references.

## VFS Integration

Path-bound sockets are created and resolved through the VFS:

- `uipc_bindat()` validates `sockaddr_un`, copies the path, runs `namei()` with `CREATE`, starts a write transaction with `vn_start_write()`, creates a `VSOCK` vnode via `VOP_CREATE()`, and associates it with the PCB using `VOP_UNP_BIND()`.
- `unp_connectat()` resolves a pathname with `namei()`, requires `vp->v_type == VSOCK`, checks MAC and `VOP_ACCESS(VWRITE)`, then obtains the bound PCB with `VOP_UNP_CONNECT()`.
- `uipc_close()`, `uipc_detach()`, and `vfs_unp_reclaim()` detach vnode state through `VOP_UNP_DETACH()` and release vnode references carefully under the vnode mtxpool lock.
- `vfs_unp_reclaim()` is the VFS callback used before reclaiming socket-type vnodes; it clears the PCB vnode pointer and drops the active vnode reference if needed.

This file is therefore a major example of IPC/VFS namespace coupling in FreeBSD.

## Socket Lifecycle

- `uipc_attach()` initializes socket buffers differently for datagram versus stream/seqpacket sockets, allocates a `unpcb`, assigns fake inode numbers, and links the PCB into the relevant global list.
- `uipc_bind()` and `uipc_bindat()` create filesystem namespace endpoints.
- `uipc_connect()` and `uipc_connectat()` connect path-based sockets; `uipc_connect2()` handles socketpair-style direct connections.
- `uipc_listen()` checks binding and state, snapshots listener credentials, and invokes socket-layer listen setup.
- `uipc_close()` disconnects peer state and detaches any bound vnode.
- `uipc_detach()` disposes queued rights, unlinks the PCB globally, detaches vnode/peer/referrers, frees address storage, destroys socket mutexes, and schedules GC if descriptors are in flight.
- `uipc_shutdown()` handles POSIX and historical behavior differences, including datagram shutdown wakeups.

## Stream and Seqpacket I/O

`uipc_sosend_stream_or_seqpacket()` bypasses the sender socket buffer and appends mbufs directly to the peer receive buffer:

- Internalizes control data before enqueue.
- Adds credentials once or persistently depending on `LOCAL_CREDS` options.
- Handles blocking, nonblocking, low-water behavior, and peer receive-buffer space.
- Uses `mchain` helpers for copyin and splitting when the receiver has partial room.
- Tracks AIO interactions through `SB_AIO_RUNNING` and `UXST_PEER_AIO`.
- Honors `MSG_EOR` for seqpacket framing.

`uipc_soreceive_stream_or_seqpacket()`:

- Waits for available data/control unless nonblocking.
- Separates leading control mbufs from data.
- Supports `MSG_PEEK`, `MSG_WAITALL`, and `MSG_EOR`.
- Externalizes `SCM_RIGHTS` on real receive.
- Contains a notable historical caveat: with `MSG_PEEK`, control mbufs are copied without externalization, and the comment notes this can expose kernel pointers in copied control data.

Poll/kqueue support for stream/seqpacket sockets is custom because writability depends on peer receive-buffer space, not local send-buffer space.

## Datagram I/O

`uipc_sosend_dgram()` builds datagram records as:

1. sender address mbuf,
2. optional control mbufs,
3. data mbufs.

Key behavior:

- Enforces `unpdg_maxdgram`.
- Uses connected sender socket buffers for connected datagram sockets.
- Uses destination receive buffer directly for unconnected `sendto()`-style sends.
- Maintains aggregate receive-buffer accounting so generic readiness APIs still work.
- Prioritizes infrequent connected senders by inserting newly active connected send buffers at the head of the receiver connection list.

`uipc_soreceive_dgram()`:

- Prioritizes previously peeked datagrams.
- Then prioritizes connected peer queues.
- Then handles unconnected receive-buffer datagrams.
- Supports `MSG_PEEK` with `uipc_peek_dgram()`.
- Externalizes control messages before copying out payload data.
- Handles truncation reporting through `MSG_TRUNC`.

`unp_disconnect()` has datagram-specific queue handling: queued connected datagrams may be moved into the receiver’s direct queue if safe, or discarded to avoid starvation/blocking scenarios.

## Descriptor Passing and Credentials

`unp_internalize()` converts userland control messages into kernel control mbufs:

- `SCM_RIGHTS`: validates file descriptors, checks `DFLAG_PASSABLE`, holds files, copies capability rights, increments in-flight counts, and stores `struct filedescent *` entries in control data.
- `SCM_CREDS`: creates credential control messages.
- `SCM_TIMESTAMP`, `SCM_BINTIME`, `SCM_REALTIME`, `SCM_MONOTONIC`: generate time control messages.
- Invalid or unsupported control types return `EINVAL`.

`unp_externalize()` converts kernel `SCM_RIGHTS` back into user descriptors:

- Allocates local fd numbers.
- Installs held files into the receiver’s file table.
- Applies `O_CLOEXEC`, `O_CLOFORK`, and jail-bound `O_RESOLVE_BENEATH` restrictions.
- Marks returned control as `MT_EXTCONTROL`.
- Frees rights if the receiver does not request control data or if an error path requires cleanup.

`unp_addsockcred()` prepends `SCM_CREDS` or `SCM_CREDS2` based on one-shot or persistent credential mode.

## Garbage Collection

Unix-domain sockets can be passed over Unix-domain sockets, creating unreachable cycles. This file implements a mark-style async GC:

- `unp_internalize_fp()` increments `unp_rights`, records `unp_file`, and increments `unp_msgcount` for local sockets in flight.
- `unp_externalize_fp()` decrements the in-flight accounting.
- `maybe_schedule_gc()` queues `unp_gc_task` when descriptors are in flight.
- `unp_gc()` finds candidates whose file refcount equals `unp_msgcount`, marks them `UNPGC_DEAD`, scans socket buffers for rights, removes internal references, restores reachable candidates, then disposes and drops truly unreachable sockets.
- `unp_dispose()` drains socket buffers while setting `UNPGC_IGNORE_RIGHTS` to synchronize with GC.
- `unp_scan()` is the generic scanner over mbuf chains and `SCM_RIGHTS` entries.

Deferred close handling avoids arbitrary recursion depth when closing sockets received through `SCM_RIGHTS`.

## Concurrency and Locking Notes

The file documents and enforces a nuanced lock hierarchy:

- Global linkage rwlock for lists, generation counts, GC flags.
- Deferred/ref-list lock for datagram ref lists and deferred closes.
- Vnode mtxpool lock before PCB locks when modifying vnode association.
- Per-PCB mutexes for peer, vnode, address, and connection state.
- Pair locking uses address ordering via `unp_pcb_lock_pair()`.
- `unp_pcb_lock_peer()` may drop and reacquire locks while holding references and using `unp_pairbusy`/`UNP_WAITING` to prevent reconnect races.

Important state flags include `UNP_CONNECTING`, `UNP_BINDING`, credential flags, GC flags, and buffer-specific flags such as `UXST_PEER_AIO`.

## Exposed Tunables and Diagnostics

Sysctls expose:

- Stream send/receive space.
- Datagram max datagram and receive space.
- Seqpacket max and receive space.
- File descriptors in flight.
- Deferred close count.
- PCB lists by socket type.
- Socket count, GC task count, and recycled socket count.

With `DDB`, `show unpcb` prints PCB, refs, address, credentials, flags, and refcount.

## Research Relevance

This file is highly relevant for filesystem research because it shows how a socket protocol participates in the filesystem namespace through VSOCK vnodes, how VFS callbacks bind and reclaim IPC endpoints, and how file-descriptor capabilities and vnode-backed objects cross process boundaries through socket buffers. It is also a dense FreeBSD example of kernel reference-cycle collection, socket-buffer specialization, and lock ordering around VFS and IPC objects.
