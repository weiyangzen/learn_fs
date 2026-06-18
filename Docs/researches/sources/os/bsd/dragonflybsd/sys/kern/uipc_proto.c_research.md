# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_proto.c

## Summary
Defines the AF_LOCAL protocol domain and its protocol switch entries.

## Main Responsibilities
- Declares `localsw` entries for `SOCK_STREAM`, `SOCK_SEQPACKET`, and `SOCK_DGRAM`.
- Binds local-domain sockets to `uipc_usrreqs`.
- Hooks local-domain initialization and descriptor-passing helpers through `unp_init`, `unp_externalize`, and `unp_dispose`.
- Registers the domain with `DOMAIN_SET(local)`.
- Creates sysctl nodes under `net.local`.

## Important Behavior
Stream and seqpacket local sockets are connection-required, support rights passing, and use synchronous ports. Seqpacket and datagram sockets are atomic; datagram sockets also set `PR_ADDR`.

## Risks
This file is small but defines protocol flags consumed throughout socket and unix-domain code. Flag changes can alter synchronization, rights passing, atomic delivery, and address semantics for all AF_LOCAL sockets.
