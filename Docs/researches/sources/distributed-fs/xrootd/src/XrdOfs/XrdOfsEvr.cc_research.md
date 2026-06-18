# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsEvr.cc

## Purpose

This file implements the OFS event receiver used for dynamic staging notifications. It creates an admin FIFO, receives external stage events, correlates them with clients waiting through callback replacement, updates balancer state, and dispatches completion callbacks.

## Important APIs, types, and functions

`Init(XrdSysError*)` creates the FIFO at `$XRDADMINPATH/ofsEvents`, exports it as `XRDOFSEVENTS`, and stores its file descriptor. `Init(XrdCmsClient*)` starts the receiver and flusher threads. `recvEvents()` reads FIFO lines and dispatches known event names. `eventStage()` parses `stage {OK|ENOENT|BAD} <path> [msg]`. `Wait4Event()` replaces the caller's error callback with `theClient`, and `Work4Event()` adds that client to the event hash or immediately sends a preposted event. `sendEvent()` invokes original callbacks with `SFS_OK` or `SFS_ERROR`.

## Control flow

Initialization is two-phase: the FIFO must exist before the CMS/balancer object is available. The receive thread attaches `msgFD` to `eventFIFO` and loops on `GetLine()`. Stage events update `OfsStats`, derive an error message, notify the balancer with `Added()` or `Removed()`, then either prepost a `theEvent` in `Events` or satisfy waiting clients. Client wait setup avoids a race by replacing callbacks before the wait response goes back to the client.

The flush thread waits on `mySem` and periodically deletes deferred clients and scrubs hash entries. Events remain in the hash for `maxLife` so clients that arrive slightly after the external event can still be resumed.

## State and persistence behavior

State is in-memory: `Events` maps path to `theEvent`, `deferQ` delays deletion of first callback clients, `runQ` prevents duplicate flusher posts, and `eventFIFO` owns the FIFO stream. The FIFO path is durable in the admin filesystem, but event records are not persisted.

## Dependencies and integration points

The file integrates with `XrdOucErrInfo` callbacks, `XrdCmsClient` balancer notifications, `XrdNetSocket` FIFO creation, `XrdOucStream`, `XrdSysThread`, `XrdSysTimer`, `OfsStats`, and OFS tracing. External stage helpers communicate by writing event lines to the exported FIFO.

## Risks and test signals

The callback/hashing logic is concurrency-sensitive. Preposted events, duplicate callbacks, deferred deletion, and destructor-triggered FIFO close should be tested under races. `BAD` and invalid statuses increment `numSeventOK`, which may be intentional legacy behavior or a stats bug. `XrdOfsScrubScan()` is currently a no-op, so hash expiry relies on `XrdOucHash` TTL semantics. Tests should cover FIFO creation failures, missing `XRDADMINPATH`, malformed event lines, balancer updates, prepost-before-wait, wait-before-event, and callback de-duplication.
