# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.cc

## Purpose

This file implements the core xroot protocol lifecycle: plugin entry points, handshake recognition, request read/dispatch, request-signature verification, response stream setup, connection recycle, stat formatting, buffer exchange, and continuation-based socket reads.

## Important APIs, types, and functions

Extern C entry points `XrdgetProtocol()` and `XrdgetProtocolPort()` initialize the protocol in some build modes. `Match()` validates the initial client handshake and binds a pooled `XrdXrootdProtocol` to an `XrdLink`. `Process()` reads request headers and arguments, `Process2()` dispatches by request code, and `ProcSig()` reads `kXR_sigver` payloads. `Recycle()`, `Cleanup()`, and `Reset()` own connection teardown/reuse. `getData()`, `getDataCont()`, `getDataIovCont()`, and `getDumpCont()` implement slow-link continuations. `Buffer()`, `Claim()`, `Swap()`, and `Reclaim()` implement `XrdSfsXio`.

## Control flow

`Match()` peeks for the xroot handshake, sends a protocol response, consumes the handshake, initializes entity/link/response state, and increments match stats. `Process()` first resumes partial reads or prior operations, then reads a `ClientRequest`, stores a copy for signature verification when needed, unmarshals byte order, reads non-write argument data, and calls `Process2()`. `Process2()` enforces signatures, requires login except for login/protocol/bind, handles high-volume file-handle operations first, permits ping/protocol without authentication, then dispatches authenticated operations and redirects selected clients before filesystem work.

## State and persistence behavior

The file defines many static process configuration values: filesystem pointers, security services, TLS policy, async limits, redirect tables, buffer sizes, stats, and global protocol object pool. Per-link state includes link pointer, file table, monitor info, request/response buffers, signature state, async counters, stream binding state, page-write state, and `ReqID`. There is no persistent storage here; durable effects occur through filesystem calls in request handlers outside this file.

## Dependencies and integration points

It depends on XRootD link/buffer/scheduler/stat/security/TLS/SFS libraries, protocol structs from `XProtocol`, monitoring, file tables, async/page-write helpers, and tracing. It is the integration hub for request execution files such as `XrdXrootdXeq.cc`, async I/O, callbacks, transit bridging, and admin/configuration support.

## Risks and edge cases

The continuation state machine is subtle: `Resume`, `myBlen`, `gdCtl.Status`, and callbacks must stay consistent on slow links and disconnects. Signature verification depends on preserving the original request before byte-order mutation. Bound-stream recycle waits for subordinate activity and can deadlock if stream state is not signaled correctly. Static configuration is process-wide, so tests must isolate it carefully.

## Test signals

High-value signals include handshake accept/reject, request dispatch before/after login, negative data length rejection, signed request success/failure/ignored paths, slow partial argument reads, iovec continuation, dump/discard continuation, recycle during blocked reads, stream verification, and stats synchronization.
