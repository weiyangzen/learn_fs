# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_proto.c

This small file declares the UNIX/PF_LOCAL protocol switch table and domain object. `DOMAIN_DEFINE(unixdomain)` places the domain in the domain linker set consumed by `uipc_domain.c`.

`unixsw[]` defines three local-domain socket protocol entries backed by `unp_usrreqs`: `SOCK_STREAM`, `SOCK_DGRAM`, and `SOCK_SEQPACKET`. Stream sockets require connections, want receive notifications, support descriptor rights, and support listen. Datagram sockets are atomic, include source addresses, and support descriptor rights. Seqpacket combines connection/listen semantics with atomic message boundaries. All three use `uipc_ctloutput` for protocol control output.

`unixdomain` sets `AF_LOCAL`, the name `unix`, domain initialization via `uipc_init`, descriptor-rights externalization/disposal via `unp_externalize` and `unp_dispose`, and the `unixsw` range. The file is therefore declarative glue between generic domain initialization and the UNIX-domain socket implementation in the `uipc_usrreq`/`unpcb` layer.

Key dependencies: `sys/domain.h`, `sys/protosw.h`, `sys/un.h`, raw control block declarations, and UNIX-domain request/control functions defined elsewhere. Risk is low in this file itself; behavioral changes here alter which semantics generic socket code applies to PF_LOCAL sockets, especially record atomicity, address/control-message handling, and SCM_RIGHTS support.
