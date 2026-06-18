# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSocket.cc

## Purpose
`XrdNetSocket.cc` implements a thin socket wrapper for creating, opening, accepting, configuring, and naming TCP/UDP/Unix sockets and local FIFOs.

## Important APIs, Types, and Functions
Core methods are the constructor, `Accept()`, `Close()`, `Create()`, `Detach()`, `Open()`, `Peername()`, `SockData()`, `SockName()`, `socketPath()`, and static `setOpts()`, `setWindow()`, `getWindow()`. Global keepalive tunables live in `XrdNetSocketCFG`.

## Control Flow
`Open()` resolves the endpoint into `SockInfo`, creates the descriptor, sets socket options, optionally sets window sizes, then binds/listens for servers or connects for clients, including timeout support for TCP. `Accept()` optionally polls before accepting and always uses XrdSys FD wrappers. `Create()` builds a filesystem path, creates a FIFO or Unix socket, and returns an owned wrapper. `setOpts()` handles close-on-exec yielding, UDP early return, linger, keepalive, Linux inherited TCP keepalive tunables, and `TCP_NODELAY`.

## State and Persistence
Each wrapper owns at most one FD plus `SockInfo`, an optional error route, and last error code. `Detach()` transfers FD ownership to the caller. Filesystem sockets/FIFOs persist as pathnames outside object lifetime unless unlinked by server setup.

## Dependencies and Integration Points
The implementation depends on `XrdNetAddr`, `XrdNetConnect`, `XrdNetOpts`, `XrdNetUtils::ProtoID()`, `XrdOucUtils::makePath()`, and XrdSys FD/platform helpers. It is used across CMS, XrdInet, XrdOfs eventing, admin sockets, bandwidth logging, and transfer daemons.

## Risks and Test Signals
Risks include platform differences for Unix sockets/FIFOs, close-on-exec semantics, partial option failure being nonfatal in `Open()`, use of `chmod()` after bind, path length handling, and `getWindow()` logging `"set socket RCVBUF"` in a getter. Tests should cover server/client TCP and UDP, Unix sockets, FIFO creation, timeout accept/connect, detach ownership, socket option failures, window sizing, path creation/access errors, and repeated `Open()` on busy wrappers.
