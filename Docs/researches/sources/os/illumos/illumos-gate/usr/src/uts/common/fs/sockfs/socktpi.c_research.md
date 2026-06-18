# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.c

## Purpose
Implements the TPI/STREAMS-backed sockfs socket backend for illumos. It creates and initializes TPI socket sonodes, maps BSD socket operations onto TPI primitives and STREAMS operations, handles AF_UNIX pathname sockets, supports direct TCP/UDP fast paths, and provides fallback conversion between non-STREAMS sockets and TPI sockets.

## Key Responsibilities
- Creates and destroys TPI `sonode` instances through `sotpi_create`, `sotpi_destroy`, `socktpi_init`, and the `sotpi_smod_create` socket-module entry.
- Opens the transport stream in `sotpi_init`, detects clone opens, configures socket-aware stream flags, discovers provider information, negotiates direct-call support, initializes stream state, and applies wildcard protocol selection.
- Implements bind/listen/unbind through `sotpi_bindlisten`, `sotpi_bind`, `sotpi_unbind`, and `sotpi_listen`, including implicit binds, AF_INET/AF_INET6 port/address handling, AF_UNIX filesystem vnode creation, rebinding for listen backlog changes, and cached local-address invalidation.
- Implements connection lifecycle through `sotpi_connect`, `sodisconnect`, `sotpi_accept`, `sotpi_shutdown`, and `so_unix_close`.
- Implements `recvmsg` translation in `sotpi_recvmsg`, converting `T_DATA_IND`, `T_UNITDATA_IND`, `T_OPTDATA_IND`, and `T_EXDATA_IND` into socket receive semantics, ancillary data, source addresses, `MSG_TRUNC`, `MSG_EOR`, `MSG_WAITALL`, `MSG_PEEK`, and urgent-data behavior.
- Implements send paths through `sotpi_sendmsg`, `sosend_dgram`, `sosend_dgramcmsg`, `sosend_svc`, `sosend_svccmsg`, `sotpi_sendmblk`, and `kstrwritemp`, including datagram destination selection, connected datagram errors, ancillary data, file-descriptor passing, out-of-band data, `MSG_DONTROUTE`, sendfile mblk writes, and stream/datagram TPI primitive construction.
- Provides direct fast paths in `sodgram_direct` and `sostream_direct` that call UDP/TCP write-side functions directly when flow control and stream state allow, falling back to normal STREAMS writes when needed.
- Implements `sotpi_getpeername`, `sotpi_getsockname`, `sotpi_getsockopt`, and `sotpi_setsockopt`, mixing sockfs-cached values with TPI option/name ioctls.
- Handles socket and STREAMS ioctls in `sotpi_ioctl` and `socktpi_plumbioctl`, including the virtual `sockmod` view, `I_PUSH`/`I_POP` transitions, async/pgrp controls, `SIOCATMARK`, and peer credential retrieval.
- Implements socket poll semantics in `sotpi_poll` on top of stream-head polling while accounting for connection state, queued connection indications, shutdown, socket errors, and urgent-data state.
- Supports fallback conversion with `sotpi_convert_sonode`, `sotpi_revert_sonode`, and `sotpi_update_state`.

## Concurrency and Lifetime
The main socket lock `so_lock` protects `so_state`, cached addresses, urgent-data counters, delayed errors, and many TPI state transitions. `SOLOCKED` serializes whole-socket control operations; `SOREADLOCKED` serializes receive paths, especially urgent-data and mark handling. `sti_plumb_lock` serializes stream plumbing ioctls so the virtual `sockmod` state and actual module stack do not diverge.

The file carefully drops `so_lock` around blocking STREAMS operations such as `kstrputmsg`, `strioctl`, `strclose`, and memory allocation, then revalidates or restores state afterward. AF_UNIX bound pathname sockets maintain a cross-link between the filesystem vnode and socket stream via `sti_ux_bound_vp` and `v_stream`; close/unbind paths must tear that down before the stream head disappears.

## Filesystem Relevance
AF_UNIX bind creates an underlying filesystem `VSOCK` vnode for pathname sockets and stores it in `sti_ux_bound_vp`. The file also maintains sockfs vnode stream state, exposes socket-specific `stat` timestamps through `sotpi_info_t`, and supports sendfile through kernel mblk writes. It is the main bridge between the VFS-visible socket vnode and TPI/STREAMS transport providers.

## Edge Cases and Risks
The code is state-machine heavy. Small changes can break socket compatibility around implicit bind, listen rebinding, nonblocking connect, datagram reconnect/unconnect, shutdown half-close behavior, `SO_DGRAM_ERRIND`, `MSG_WAITALL`, and urgent-data marks. AF_UNIX address translation is particularly subtle because external pathname addresses and internal transport vnode-addresses coexist, with `sti_faddr_noxlate` changing behavior across connect, accept, close, send, and getpeername. Direct TCP/UDP fast paths must preserve STREAMS error, flow-control, auditing, and partial-write semantics when falling back.
