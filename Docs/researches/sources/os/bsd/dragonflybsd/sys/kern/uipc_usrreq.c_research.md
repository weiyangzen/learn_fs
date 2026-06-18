# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_usrreq.c

## Role

This file implements the AF_LOCAL/Unix-domain socket protocol request layer. It provides `uipc_usrreqs`, local socket attach/bind/connect/listen/send/receive-side notification/shutdown/address operations, local socket PCB lifecycle, pathname socket lookup, peer credentials, descriptor passing through `SCM_RIGHTS`, credential passing through `SCM_CREDS`, and garbage collection for Unix-domain sockets referenced only by in-flight rights.

It plugs into the generic socket layer through protocol `pru_*` callbacks. Generic send/receive behavior still comes from `sosend()` and `soreceive()`; this file handles what those sends and receives mean for local sockets.

## Global State And Synchronization

The file maintains separate global PCB lists for stream, datagram, and seqpacket local sockets, each with a count. `unp_token` protects global Unix-domain topology, while per-UNPCB pool tokens protect individual PCB/socket links. `unp_rights_token` protects in-flight descriptor accounting.

Important flags include:

- `UNP_DETACHED`: PCB has been detached from the active global list.
- `UNP_CONNECTING`: connect is in progress.
- `UNP_DROPPED`: drop processing has completed.
- `UNP_MARKER`: marker PCB used for safe list iteration.
- `UNPGC_REF`, `UNPGC_DEAD`, `UNPGC_SCANNED`: garbage-collection mark/sweep state.

The comments specify a key locking invariant: changes to `unp_conn` require both `unp_token` and the per-UNPCB pool token, and acquiring `so_pcb` must be validated after taking the pool token.

`unp_getsocktoken()` loops until it obtains the pool token for the current `so_pcb` and verifies the pointer did not change. `unp_reference()`/`unp_free()` manage PCB references; the final `unp_free()` calls `unp_detach()`.

## Protocol Request Table

`uipc_usrreqs` maps protocol operations to this file:

- abort, accept, attach, bind, connect, connect2, detach, disconnect, listen, peeraddr, rcvd, send, sense, shutdown, sockaddr
- unsupported control and OOB receive operations
- generic `sosend` and `soreceive` for user I/O

Most request handlers acquire the necessary tokens, validate `UNP_ISATTACHED()`, call the internal helper, release tokens, and reply to the netmsg.

`uipc_ctloutput()` supports `LOCAL_PEERCRED` getsockopt for sockets with cached peer credentials. It returns `ENOTCONN` for stream/seqpacket sockets without credentials and `EINVAL` for datagram sockets without credentials; setting local options is unsupported.

## Attach, Detach, Bind, And Listen

`unp_attach()` reserves default send/receive space according to socket type when not already reserved. Defaults are controlled by sysctls under `net.local.stream`, `net.local.dgram`, and `net.local.seqpacket`, all based on `PIPSIZ` unless overridden. Stream sockets set `SSB_STOPSUPP` on send and receive buffers so sendfile and direct mbuf transfer can use stop-based backpressure.

The attach path allocates an `unpcb`, initializes reference count, generation count, references list, socket backpointer, jail root vnode pointer, stores it in `so_pcb`, takes a socket reference, and inserts it in the type-specific global list.

`unp_detach()` removes vnode binding, clears `v_socket`, releases the vnode, marks both socket sides disconnected, clears `so_pcb` and the PCB socket backpointer under required tokens, drops the socket reference, frees address and PCB storage, and schedules GC if any rights remain in flight.

`unp_bind()` creates a filesystem `VSOCK` node at the supplied `sockaddr_un` path using namecache lookup with create semantics. It rejects empty paths, already-bound PCBs, existing names, and invalid mountpoint cases. On success it stores `vp->v_socket`, the vnode, and a duplicated socket address.

`unp_listen()` caches the listener process credentials into `unp_peercred` and marks `UNP_HAVEPCCACHED`; connecting stream/seqpacket clients later use this cached credential state.

## Connect And Disconnect

`unp_find_lockref()` resolves a pathname socket while `unp_token` is held. It validates path length, looks up the vnode, requires `VSOCK`, checks write access, fetches `v_socket`, verifies matching socket type, obtains and validates the target UNPCB token, references it, and returns it locked/referenced.

`unp_connect()` handles pathname connect. It rejects already connecting or connected PCBs, marks `UNP_CONNECTING`, finds the target, and then:

- For connection-required sockets, requires a listening target with cached peer credentials, creates a child socket with `sonewconn_faddr()`, copies bound address state to the child, sets peer credentials on both sides, connects the active socket to the child PCB, and aborts the child on connect-pair failure.
- For datagram sockets, directly connects the caller to the target.

`unp_connect2()` connects two already-created sockets, used by socketpair. It verifies matching types, copies supplied credentials into both PCBs, rejects invalid/connected state, and delegates to `unp_connect_pair()`.

`unp_connect_pair()` installs `unp_conn` links. Datagram sockets insert the caller into the peer's `unp_refs` list and mark only the caller connected. Stream and seqpacket sockets install reciprocal `unp_conn` pointers and mark both sockets connected.

`unp_disconnect()` clears connection state. Datagram sockets remove the caller from the peer references list and clear connected state. Stream and seqpacket sockets clear both reciprocal connection pointers, mark both sockets disconnected, and preserve the peer PCB with a temporary reference while changing topology.

`unp_drop()` marks a PCB detached, removes it from the global type list, disconnects its active connection and any datagram sockets referencing it, marks it dropped, and releases its reference.

## Send And Receive-Side Flow Control

`uipc_send()` is the protocol send operation. It rejects OOB data, internalizes control messages, and then handles each socket type.

For datagram sockets:

- If an explicit destination address is supplied, it rejects already-connected sockets, resolves the target with `unp_find_lockref()`, then releases the target token while keeping a reference.
- If no destination is supplied, it requires an existing `unp_conn`.
- If the receiver has `SO_PASSCRED`, it ensures an `SCM_CREDS` control message is present, creating one with `sbcreatecontrol()` when needed.
- It appends sender address, payload, and control to the peer receive buffer with `ssb_appendaddr()` and wakes peer readers.

For stream and seqpacket sockets:

- It performs implied connect if a destination address is supplied and no connection exists.
- It rejects unconnected sends and sends after `SS_CANTSENDMORE`.
- It appends control+data, seqpacket records, or stream data directly to the peer receive sockbuf.
- It sets `SSB_STOP` on the sender when the peer receive buffer reaches the sender's high-water or mbuf limit, providing backpressure for direct mbuf transfer.
- It wakes peer readers.

If `PRUS_EOF` is set, send is followed by `socantsendmore()` and `unp_shutdown()`.

`uipc_rcvd()` is called when the receiver drains data. For stream/seqpacket sockets it checks whether the peer receive buffer has fallen below the sender's high-water and mbuf limits; if so, it clears `SSB_STOP` on the sender and wakes writers.

`unp_shutdown()` marks the connected peer unable to receive more for stream and seqpacket sockets.

## Address And Stat Operations

`uipc_accept()` returns the connected peer's bound address if available, otherwise a synthetic unnamed `AF_LOCAL` sockaddr.

`uipc_peeraddr()` returns the connected peer address or synthetic unnamed sockaddr. A comment notes a workaround because the original test may fail even for established connections.

`uipc_sockaddr()` returns the local bound address if one exists.

`uipc_sense()` fills `st_blksize` from send-buffer high-water and `st_dev` with `NOUDEV`.

`unp_pcblist()` implements sysctl export for active local datagram, stream, and seqpacket sockets. It uses a marker PCB to walk lists safely while `SYSCTL_OUT()` may block and temporarily release `unp_token`; it filters sockets hidden by jail root vnode mismatch and exports `xunpcb` plus `xsocket` snapshots.

## Descriptor And Credential Passing

`unp_internalize()` validates a control mbuf as `SOL_SOCKET` `SCM_RIGHTS` or `SCM_CREDS`.

For `SCM_CREDS`, it fills `struct cmsgcred` from the sending process: pid, real/effective uid/gid, and groups.

For `SCM_RIGHTS`, it validates file descriptors under the sender filedesc spinlock, rejects invalid descriptors and kqueue descriptors, expands the control mbuf when pointer-sized file references will not fit, converts integer FDs to `struct file *` pointers in reverse order, `fhold()`s each file, increments per-file `f_msgcount`, tracks Unix-domain socket PCBs in `unp_msgcount`/`unp_fp`, and increments global `unp_rights`.

`unp_externalize()` converts received `struct file *` pointers back to integer file descriptors. It first checks descriptor availability, discarding all rights if the receiver cannot fit them. It allocates descriptors, installs files with `fsetfd()`, honors `MSG_CMSG_CLOEXEC` and `MSG_CMSG_CLOFORK`, handles revoked files by installing a fresh placeholder file when possible, decrements in-flight rights through `unp_del_right()`, drops file references, and shrinks the control message length from pointer-sized entries to integer FD entries.

`unp_dispose()` scans an mbuf chain for `SCM_RIGHTS` and discards each referenced file. `unp_scan()` walks records and control mbufs, applying a callback to every file pointer in the first rights control message found per record.

`unp_discard()` decrements rights accounting, then either defers `fdrop()` for Unix-domain socket files to a dedicated taskqueue to avoid deep recursive discard chains, or drops non-local-socket files directly.

`unp_defdiscard_taskfunc()` drains the deferred discard list and performs the delayed `fdrop()` operations.

## Garbage Collection

The file contains two GC implementations. The `UNP_GC_ALLFILES` version, compiled only when that macro is set, scans all files using `FMARK`/`FDEFER`. The default implementation scans only Unix-domain PCBs and in-flight Unix-domain socket rights, matching the file header's explanation that only cyclic socket references still require GC.

Default `unp_gc()`:

1. Holds `unp_rights_token` and `unp_token`.
2. Clears all GC flags on all local PCBs.
3. Repeatedly scans global PCB lists with a marker until no new reachable sockets are found.
4. `unp_gc_process()` marks sockets that are only referenced by in-flight messages as potentially dead, and scans reachable sockets' receive buffers to mark any Unix-domain socket rights they reference as reachable.
5. If unreachable sockets exist, it gathers bounded batches of files for PCBs marked `UNPGC_DEAD`, takes extra references, calls `sorflush()` to dispose rights queued on those sockets, then drops the extra references.

The long GC comment explains why simply dropping each in-flight reference is unsafe: cycles of sockets carrying references to each other can recursively close sockets already in `SS_NOFDREF` transition. The extra-reference plus `sorflush()` approach breaks rights cycles without reentering close paths incorrectly.

## Initialization And Sysctls

`unp_init()` initializes global PCB lists, deferred-discard structures, GC task, marker PCB, and a dedicated Unix-domain taskqueue pinned to the last CPU.

Sysctls expose in-flight descriptor count and default buffer sizes/max datagram sizes for local stream, datagram, and seqpacket sockets, plus per-type PCB lists.

## Notable Assumptions And Risks

- The code relies heavily on token ordering: `unp_token` plus per-UNPCB pool tokens for topology, and `unp_rights_token` for descriptor accounting.
- `unp_getsocktoken()` must revalidate `so_pcb` after acquiring a token; using raw `so_pcb` without this pattern can race detach.
- Pathname bind/connect use vnode `v_socket` as the live socket link, so detach must clear it under the global topology token.
- Descriptor passing stores kernel file pointers inside mbufs until externalized; all rights paths must keep `f_msgcount`, `unp_msgcount`, `unp_fp`, and `unp_rights` balanced.
- Direct mbuf transfer between local stream sockets requires `SSB_STOP`/`uipc_rcvd()` flow control to prevent unbounded queued mbufs.
- Deferred discard exists to flatten recursive close/dispose chains involving Unix-domain sockets passed over Unix-domain sockets.
