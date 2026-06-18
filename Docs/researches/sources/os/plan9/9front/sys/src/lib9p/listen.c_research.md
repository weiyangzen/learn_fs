# File Research: sources/os/plan9/9front/sys/src/lib9p/listen.c

## Read Status
Complete: 118 lines read.

## Purpose
Adds network-listening support for lib9p servers. It announces a network address, accepts connections, clones the server template, and runs each connection as a 9P service.

## Main Responsibilities
- Duplicate an input `Srv` as a listener template.
- Announce and listen on a Plan 9 network address.
- Accept client connections.
- Create per-connection `Srv` instances with separate fd state.
- Determine remote system name from the network directory.
- Free per-connection resources on server close.

## Important Functions
- `listensrv`: prepares a listener `Srv` and starts `listenproc`.
- `listenproc`: announce/listen/accept loop.
- `srvproc`: invokes `srv`.
- `srvfree`: closes connection fd and frees address/server copy.
- `getremotesys`: reads `ndir/remote` and extracts the remote system component.

## Dependencies and Interactions
- Uses Plan 9 network primitives: `announce`, `listen`, `accept`.
- Uses `Srv.forker`, defaulting to `srvforker`, so callers can choose process or thread-style execution.
- Each accepted connection runs through the common `srv.c` service loop.
