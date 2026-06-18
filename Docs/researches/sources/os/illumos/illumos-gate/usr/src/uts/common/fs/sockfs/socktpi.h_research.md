# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/socktpi.h

## Purpose
Defines the TPI-specific private state stored behind `sonode.so_priv` and declares the public-internal TPI socket entry points used by sockfs and related modules.

## Key Elements
`struct soaddr` wraps cached socket addresses with allocated length metadata. `sotpi_info_t` stores the TPI socket state: transport device, original sockparams for fallback, plumbing lock, ack CV, cached local/foreign addresses, TPI provider capabilities, preallocated unbind message, pending ack and disconnect messages, connection indication queue, delayed datagram errors, timestamps, urgent-data counters, direct-call state, and AF_UNIX pathname/internal address state.

The header documents AF_UNIX pathname socket binding: sockfs creates a `VSOCK` vnode in the underlying filesystem while using `v_stream` linkage to find the bound socket. It also documents urgent-data handling through `sti_oobcnt`, `sti_oobsigcnt`, `T_EXDATA_IND`, `MSGMARK`, `MSGMARKNEXT`, `MSGNOTMARKNEXT`, and stream-head mark flags.

## Dependencies
Depends on socket, TPI, STREAMS, and sockfs types such as `sonode`, `sockparams`, `mblk_t`, `t_uscalar_t`, `T_capability_ack`, and `so_ux_addr`.

## Behavior/Risks
This header is the internal contract for TPI sockets. Field validity bits drive `getsockname`/`getpeername` caching, AF_UNIX translation, fallback conversion, and direct transport calls. The urgent-data comments describe behavior that must remain consistent with `strsock_proto`, stream-head mark handling, `sotpi_recvmsg`, `SIOCATMARK`, and poll/select behavior.
