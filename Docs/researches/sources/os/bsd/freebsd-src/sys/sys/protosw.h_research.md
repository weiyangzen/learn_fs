# File Research: sources/os/bsd/freebsd-src/sys/sys/protosw.h

Read completely: 183 lines.

## Purpose
Defines the socket protocol switch table KPI used by domains/protocols to plug protocol operations into the socket layer.

## Main Elements
- Declares protocol operation typedefs for attach/detach, bind/connect/listen/accept, send/receive, sendfile readiness, control operations, polling, kqueue, AIO, shutdown, address queries, labels, fd close, and chmod.
- Defines `pr_send_flags_t` including OOB, EOF, more-to-come, not-ready, and IPv6 flags.
- Defines `struct protosw` with socket type, protocol number, flags, domain pointer, and function pointers grouped by cache-line comments.
- Defines protocol behavior flags such as `PR_ATOMIC`, `PR_ADDR`, `PR_CONNREQUIRED`, `PR_WANTRCVD`, `PR_IMPLOPCL`, `PR_CAPATTACH`, and `PR_SOCKBUF`.
- Declares domain/protocol lookup and registration functions plus known `inetdomain` and `inet6domain`.

## Dependencies And Integration
Used by network domains, socket creation and dispatch, sendfile/KTLS readiness callbacks, socket buffer policy, Capsicum attach rules, MAC labeling, AIO, kqueue, and protocol module registration.

## Risk Notes
Function pointer signatures and flag semantics are protocol KPI. Incorrect handler setup can break socket lifecycle, sendfile readiness, address handling, or protocol unload/register safety.
