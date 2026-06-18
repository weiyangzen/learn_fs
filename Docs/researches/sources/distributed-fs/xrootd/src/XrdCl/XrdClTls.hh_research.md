# sources/distributed-fs/xrootd/src/XrdCl/XrdClTls.hh

## Purpose

This header declares TLS support for XrdCl sockets: a global initializer and the `Tls` class that wraps encrypted I/O and handshake event translation.

## Important APIs, Types, and Functions

`InitTLS()` initializes the shared TLS context. `Tls` exposes `Connect`, `Read`, fake `ReadV`, `Send`, `Shutdown`, `MapEvent`, and `ClearErrorQueue`. Private `TlsHSRevert` tracks whether a read callback should be invoked on write readiness or a write callback on read readiness. `ToStatus` maps XrdTls return codes into XrdCl status values.

## Control Flow

The class is constructed with a `Socket` and `AsyncSocketHandler`. Callers use the same read/write style as raw sockets, but the TLS object may perform handshake steps lazily and request event remapping through `MapEvent`.

## State and Persistence Behavior

Per-instance state is nonpersistent: raw socket pointer, owned TLS socket, handshake reversal flag, and socket handler pointer. The global initializer owns context state outside the class.

## Dependencies and Integration Points

It includes XrdTls socket support, XRootD response statuses, and async socket handler declarations. `Socket` owns or uses this class when encryption is enabled.

## Risks and Edge Cases

The constructor can throw if TLS initialization fails, so callers must translate that into `XRootDStatus`. `ReadV` is not true vector I/O; it loops over buffers and can stop on retry after partial progress.

## Test Signals

Compile-level API tests plus TLS integration tests for handshake, read, write, event mapping, and shutdown validate this header.
