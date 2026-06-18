# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/sockfs/sockstr.c

## Overview
`sockstr.c` is the STREAMS/TPI-facing half of illumos sockfs. It installs stream-head hooks, initializes TPI provider capabilities, translates incoming TPI primitives into socket state changes, manages urgent/OOB data state, queues connection indications and acknowledgements, and supports temporarily exposing a socket as a plain stream when the illusory `sockmod` is popped.

## Main Responsibilities
- Convert between socket and stream modes with `so_sock2stream()` and `so_stream2sock()`.
- Install/remove stream-head protocol hooks through `so_installhooks()` and `so_removehooks()`.
- Initialize TPI metadata with `so_basic_strinit()`, `so_strinit()`, `do_tcapability()`, and `do_tinfo()`.
- Maintain socket state transitions for connect, disconnect, half-close, read/write errors, and OOB data.
- Queue and wait for TPI acknowledgement primitives and pending connection indications.
- Process inbound STREAMS messages in `strsock_proto()` and `strsock_misc()`.
- Manage async signal ownership and compatibility `getmsg`/`putmsg` wrappers.

## Key Control Flow
- `so_strinit()` installs hooks, requests `T_CAPABILITY_ACK` first, falls back to `T_INFO_REQ` when needed, copies transport limits into `sotpi_info_t`, derives `so_mode`, and allocates address buffers.
- `sowaitprim()` waits for a matching ack or `T_ERROR_ACK`, validating primitive type and minimum length before returning the message to callers.
- `strsock_proto()` is the central dispatcher for TPI primitives. It validates message type, size, and alignment, then handles data, unitdata, optdata, exdata, connect confirmation, connection indication, orderly release, disconnect, datagram errors, and ack primitives.
- `strsock_misc()` handles non-protocol STREAMS messages, notably `M_PCSIG/SIGURG`, selected flush behavior, and ignoring hangup/error messages that sockfs tracks itself.

## State and Locking
- `so_lock_single()` serialization is assumed for operations that generate TPI acks.
- `so_lock_read()` prevents concurrent receive-side processing paths from interfering, especially around STREAMS conversion and OOB handling.
- `SOASYNC_UNBIND` protects asynchronous unbind processing after disconnect; `so_save_discon_ind()` defers `T_DISCON_IND` work when another serialized operation is active.
- Connection indications are stored on `sti_conn_ind_head/tail`, while TPI acks are stored in `sti_ack_mp` and signaled through condition variables.

## Notable Behaviors
- `so_sock2stream()` strips TCP accept fast-path options from queued `T_CONN_IND` messages before moving them to the stream head.
- `so_stream2sock()` forces sleeping reads to leave, installs hooks again, flushes queued STREAMS data, and resumes socket tracking from an initial-like state.
- Connected datagram sockets filter inbound `T_UNITDATA_IND` sources for AF_INET/AF_INET6 but deliberately do not filter AF_UNIX source addresses.
- AF_UNIX close indications are encoded as options and can turn into `ECONNRESET`, `SS_CANTSENDMORE`, or discarded no-data messages depending on socket state.
- OOB handling keeps separate signal and data counters, marks `T_EXDATA_IND` messages with `MSGMARK`, stores out-of-line urgent data in `so_oobmsg`, and compresses adjacent out-of-line OOB marks to avoid stream-head flow-control buildup.

## Error Handling and Validation
- The file aggressively rejects too-short or unaligned TPI messages with warnings and frees the offending message.
- Provider capability timeouts mark the provider as not supporting `T_CAPABILITY_REQ` and retry through `T_INFO_REQ`.
- Disconnect and datagram error reasons are treated as errno values, with zero reasons normalized to compatibility errors such as `ECONNRESET` where needed.
- `sogetrderr()` and `sogetwrerr()` provide stream-head callbacks that clear or preserve socket errors depending on peek behavior.

## Dependencies
- Uses STREAMS APIs such as `strsetrputhooks`, `kstrputmsg`, `strseteof`, `strsetrerror`, `strsetwerror`, `strgetmsg`, and `strputmsg`.
- Shares socket structures and helpers from `socktpi_impl.h`, including `sotpi_info_t`, `SOTOTPI()`, and socket state flags.
- Relies on helpers from `socksubr.c` for option parsing, OOB verification, address formatting in debug builds, and lock helpers.

## Research Notes
This file is the main compatibility bridge between BSD-style socket semantics and TPI/STREAMS transport providers. Its highest-risk areas are deferred disconnect/unbind sequencing, OOB counter invariants, datagram source filtering, and the distinction between ordinary socket mode and stream-exposed mode.
