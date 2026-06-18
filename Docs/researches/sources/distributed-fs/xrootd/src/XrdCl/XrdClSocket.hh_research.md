# sources/distributed-fs/xrootd/src/XrdCl/XrdClSocket.hh

## Purpose

This header declares `XrdCl::Socket`, the client-side network socket abstraction used by asynchronous stream handlers and the TLS layer. It wraps a file descriptor, connection state, address/name caching, raw read/write operations, socket options, poll-based readiness, corking, TLS handshakes, and event mapping.

## Important APIs, Types, and Functions

`SocketStatus` distinguishes disconnected, connected, and connecting states. Construction can adopt an existing descriptor or start disconnected. `Initialize`, `Connect`, `ConnectToAddress`, `Close`, `Poll`, `ReadRaw`, and `WriteRaw` form the blocking/raw I/O surface. `Send` has overloads for plain buffers, `XrdSys::KernelBuffer`, and XrdCl `Message`. `Read`, `ReadV`, and `ClassifyErrno` provide lower-level helpers that map transient `EAGAIN`/`EWOULDBLOCK` to retry statuses. TLS-specific methods are `TlsHandShake`, `IsEncrypted`, `MapEvent`, `Cork`, `Uncork`, and `Flash`.

## Control Flow

The typical flow is initialize or adopt a descriptor, connect to a host or resolved `XrdNetAddr`, then let `AsyncSocketHandler` drive `Read`, `ReadV`, and `Send` through poller callbacks. `Poll` guards timeout and readiness decisions for raw reads/writes. If TLS is enabled, the socket delegates reads/writes/event mapping to `Tls`, and corking is used to handle SSL/TLS write limitations around vector writes.

## State and Persistence Behavior

State is in memory only: descriptor, status, server address, cached local/peer/name strings, protocol family, channel ID pointer, corked flag, and optional `Tls` object. There is no persistence; descriptor ownership and close timing are the main lifecycle concerns.

## Dependencies and Integration Points

The header integrates with `XrdClXRootDResponses` for `XRootDStatus`, `XrdNetAddr` for resolved endpoints, `XrdSysKernelBuffer`, `Message`, `AnyObject` channel IDs, `Tls`, and `AsyncSocketHandler`. It is consumed by `Stream`, socket handlers, and TLS handshake code.

## Risks and Edge Cases

Correctness depends on the implementation consistently mapping errno and socket readiness into retryable versus fatal statuses. TLS event remapping can invert read/write readiness during handshakes, so poller callbacks must honor `MapEvent`. Cached name fields are mutable and can become stale after reconnects unless invalidated by implementation code. Callers can manually mutate status through `SetStatus`, which is intentionally dangerous.

## Test Signals

Useful signals include connection timeout tests, nonblocking `EAGAIN` retry behavior, remote disconnect classification, SIGPIPE-free send behavior, cork/uncork behavior, and TLS handshake/event-remap integration through `AsyncSocketHandler`.
