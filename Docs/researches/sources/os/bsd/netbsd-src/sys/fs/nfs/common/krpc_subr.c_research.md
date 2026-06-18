# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/krpc_subr.c

## Purpose
Implements a small kernel UDP SunRPC client for NFS diskless bootstrapping. It is simpler than the main reconnecting NFS RPC layer and is used for portmapper/mountd calls during early NFS-root setup.

## Main Interfaces
- `krpc_portmap` builds a portmapper `GETPORT` request and calls `krpc_call`; it special-cases the portmapper program itself to return port 111.
- `krpc_call` creates a UDP socket, sets receive timeout, optionally enables broadcast, binds a reserved local port, prepends an AUTH_UNIX-root RPC header, retransmits with increasing timeout, validates replies by xid/direction/status, strips the RPC reply header, and returns the result mbuf.
- `xdr_string_encode` encodes a counted, padded XDR string into an mbuf.

## Protocol Details
- Uses AUTH_UNIX credentials with root-like empty host/group fields and AUTH_NULL verifier.
- Supports only `AF_INET`/UDP.
- Uses a static monotonically increasing xid.
- Retransmit delay grows up to `MAX_RESEND_DELAY`, then prints timeout messages.
- Handles RPC accept errors, program mismatch, and status errors, but keeps retrying for many denial/status cases unless a hard mismatch is detected.

## Dependencies
Uses kernel socket APIs (`socreate`, `sosetopt`, `sobind`, `sosend`, `soreceive`, `soclose`), mbuf APIs, XDR byte-order helpers, and constants from `krpc.h`.

## Risks
- Not a general-purpose RPC layer: IPv4-only, UDP-only, AUTH_UNIX-only.
- Static xid is not explicitly synchronized.
- `xdr_string_encode` returns `NULL` for strings larger than one cluster but callers must handle that.
- Long retry loop is intended for bootstrapping but can block boot progress on unreachable servers.
