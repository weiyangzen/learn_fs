# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.hh

## Purpose

This header declares `XrdOfsEvr`, the dynamic staging event receiver. It exposes initialization, event receiving/flushing, client wait registration, and callback work handling.

## Important APIs, types, and functions

`Init(XrdSysError*)` and `Init(XrdCmsClient*)` split FIFO setup from thread/balancer setup. `Wait4Event()` registers a client for a path by replacing the error callback. `Work4Event()` is invoked by the nested `theClient::Done()` callback. `flushEvents()` and `recvEvents()` are thread entry targets.

`theClient` captures the original callback, callback argument, user, path, and owning `XrdOfsEvr`. `theEvent` records the final return code, final message, whether the event happened, and the waiting client list.

## Control flow

Clients first call `Wait4Event()` while issuing a wait-style response. The nested callback then calls back into `Work4Event()` after the wait is safely sent. External event lines are received by `recvEvents()`, parsed by private handlers, and fan out to waiting clients. The flusher thread handles delayed cleanup.

## State and persistence behavior

The class owns mutex/semaphore synchronization, FIFO stream state, CMS balancer pointer, deferred client queue, run flag, file descriptor, and an `XrdOucHash<theEvent>` keyed by path. State is runtime-only; event retention is bounded by `maxLife`.

## Dependencies and integration points

The header depends on `XrdOucHash`, `XrdOucErrInfo`, `XrdSysPthread`, and `XrdOucStream`, and forward-declares logging and CMS client types. It is consumed by OFS code that needs to wait for external stage completion.

## Risks and test signals

The nested callback owns raw pointers and requires stable lifetime boundaries. `Wait4Event()` transfers callback ownership into `theClient`, so tests should verify no leaks or double callbacks across immediate event, delayed event, and cancellation/destruction paths. Header-level signals include the eight-hour max life and path-based correlation, both worth regression tests.
