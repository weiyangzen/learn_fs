# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpUtil.hh

## Purpose

This header declares shared utilities for the HTTP client plugin: status conversion helpers, string trimming, curl handle construction, header parsing, the pollable operation queue, and monitoring/handle lifecycle hooks.

## Important APIs, types, and functions

Top-level utilities include `kLogXrdClHttp`, `HTTPStatusIsError`, `HTTPStatusConvert`, `ltrim_view`, `trim_view`, and `GetHandle`. `HeaderParser` exposes parsed response metadata and static helpers for canonicalization, digest parsing, base64 decode, and checksum digest names. `HandlerQueue` exposes bounded producer/consumer operations, poll FD access, easy-handle recycling, expiry, shutdown, handle cleanup, and monitoring JSON.

## Control flow

Concrete operations rely on `HeaderParser` through the base `CurlOperation` header callback. Factory and worker code rely on `HandlerQueue` as the bridge between XRootD API threads and curl worker threads; the queue can be polled by curl's event loop while still offering blocking condition-variable behavior to producers/consumers.

## State and persistence behavior

`HeaderParser` is per-operation state. `HandlerQueue` owns an in-memory deque, pipe FDs, thread-local curl-handle cache, and static counters. There is no durable persistence.

## Dependencies and integration points

The header includes checksum, options-cache, and response-info headers and forward-declares curl and XRootD classes. It is included by operation implementations, factory/filesystem/file code, and worker code.

## Risks and edge cases

`HeaderParser::MoveHeaders` is destructive and should only be called after `HeadersDone()`. `HandlerQueue::Produce` can fail an operation if it waits in a full queue past the operation expiry. Consumers must call `Shutdown` and `ReleaseHandles` during plugin unload to avoid leaving curl handles or FDs live.

## Test signals

Compile coverage should catch most declaration drift. Behavioral tests should target parser metadata, queue poll-FD synchronization, queue expiry, and monitoring counters.
