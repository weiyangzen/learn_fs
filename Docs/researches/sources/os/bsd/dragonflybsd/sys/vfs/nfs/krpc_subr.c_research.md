# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/krpc_subr.c

## Role

Implements a minimal kernel UDP SunRPC client for diskless NFS bootstrap. It performs portmapper lookups, constructs AUTH_UNIX RPC calls, binds to reserved local ports, retransmits with backoff, validates replies, strips RPC reply headers, and encodes XDR strings.

## Major Entry Points

- `krpc_portmap()` returns the UDP port for an RPC program/version using `PMAPPROC_GETPORT`, with a fast path for portmapper itself.
- `krpc_call()` sends a single RPC request, repeatedly retransmits until a valid reply arrives, and returns the decoded reply payload mbuf.
- `xdr_string_encode()` builds an mbuf containing XDR length plus padded string data.

## Implementation Notes

- The RPC code is IPv4-only and rejects non-`AF_INET` addresses.
- The socket is UDP with a one-second receive timeout; broadcast is enabled when the caller requests the response source address.
- Local binding searches downward from `IPPORT_RESERVED` so servers requiring privileged source ports accept the request.
- RPC headers are prepended in a separate mbuf containing XID, RPC version 2, program, version, procedure, AUTH_UNIX credentials, and null verifier.
- XIDs are allocated from a static counter with atomic increment and skip zero.
- Retransmission timeout grows linearly up to `MAX_RESEND_DELAY`, after which timeout messages are printed.
- Replies must have enough bytes for the minimum header, must be RPC replies, must match the XID, must be accepted, and must have success status.
- Program mismatch maps to `EBADRPC`; other denied statuses are logged and ignored until another reply or timeout.
- Accepted replies have the auth verifier skipped before the remaining mbuf payload is returned to the caller.
- `xdr_string_encode()` refuses strings that would exceed `MCLBYTES`.

## Dependencies

Uses DragonFly sockets, mbufs, socket buffers, RPC/XDR constants, portmapper constants from `krpc.h`, and kernel memory allocation.

## Research Notes

This helper is deliberately small compared with the normal NFS RPC machinery. It exists so early NFS-root code can contact portmapper and mountd before a fully mounted NFS client filesystem is active.
