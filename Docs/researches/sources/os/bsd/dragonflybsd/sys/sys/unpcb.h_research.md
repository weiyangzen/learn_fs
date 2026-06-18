# File Research: sources/os/bsd/dragonflybsd/sys/sys/unpcb.h

## Summary
Protocol control block definitions for UNIX-domain sockets.

## Main Responsibilities
- Defines `struct unpcb` links between sockets, connected peers, referencing sockets, bound address, peer credentials, file-passing state, vnodes, and generation count.
- Defines peer-credential state flags and private implementation flags.
- Defines `struct xunpcb` for diagnostic/export use when socket internals are available.

## Important Behavior
A socket can both reference another socket and be referenced by multiple sockets, so `unp_conn`, `unp_refs`, and `unp_reflink` are separate. Peer credentials may be true peer credentials or cached listen-time credentials depending on flags.

## Risks
The header notes `xunpcb` depends on `<sys/socketvar.h>`. GC and rights-passing fields are delicate because UNIX sockets can carry file references inside control messages.
