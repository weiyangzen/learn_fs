# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.hh

## Purpose
`XrdClHttpFile.hh` declares the HTTP file plugin class that implements `XrdCl::FilePlugIn`. It is the per-open-handle state container for HTTP file I/O and the declaration point for prefetch, PUT serialization, timeout, monitoring, property, and callout behavior.

## Important APIs and Types
The public interface mirrors XrdCl file operations: `Open`, `Close`, `Stat`, `Fcntl`, `Read`, `PgRead`, `VectorRead`, two `Write` overloads, `IsOpen`, `SetProperty`, and `GetProperty`. It exposes `Flags`, static timeout setters/getters, `ParseHeaderTimeout`, `GetHeaderTimeout`, federation metadata timeout accessors, and `GetMonitoringJson`.

Nested classes include `PutResponseHandler`, `PutDefaultHandler`, `PrefetchResponseHandler`, `PrefetchDefaultHandler`, and file-specific `HeaderCallout`. These declare the concurrency contracts for serialized upload and chained prefetch reads.

## Control Flow
The declaration shows two major data paths: read-side prefetch based on one long-running GET with continuations, and write-side PUT based on one curl upload that pauses between client writes. Public operations enqueue `Curl*Op` objects into the shared `HandlerQueue`.

## State and Persistence
Per-handle state includes open status, full-download flag, open flags, original/last/current URLs, shared queue, logger, property map with shared mutex, timeout values, current PUT op/handler/asize/write offset, current prefetch op/offset/size/handlers, header callout pointer, default header callout, and static prefetch counters. Remote persistence is performed by implementation-side PUT/close logic.

## Dependencies and Integration Points
The class depends on XrdCl file/plugin APIs, connection/header callout interfaces, atomics, synchronization primitives, variants, buffers, and forward-declared curl operations. `Factory` sets static timeout defaults; `CurlOpenOp` sets properties such as last URL/content length.

## Risks and Test Signals
The header exposes many raw pointers and atomics around asynchronous callbacks. Tests should focus on lifetime during close/destruction, mutex-protected property reads, header callout pointer replacement, prefetch disable checks, PUT handler queue ordering, and monitoring counter consistency.
