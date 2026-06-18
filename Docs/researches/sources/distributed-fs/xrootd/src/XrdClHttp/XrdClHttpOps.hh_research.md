# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOps.hh

## Purpose

This header defines the HTTP operation class hierarchy used by the XRootD HTTP client plugin. It declares the abstract `CurlOperation` contract and concrete operation classes for OPTIONS, stat/open/checksum/delete/mkdir/query/read/prefetch/vector-read/page-read/listdir/copy/put.

## Important APIs, types, and functions

`CurlOperation` exposes operation lifecycle (`Setup`, `FinishSetup`, `Success`, `Fail`, `ReleaseHandle`), verb identity (`HttpVerb`, `GetVerb`, `GetVerbString`), timeout checks, redirect handling, connection callout hooks, continuation queue hooks, response-info movement, curl handle access, statistics reset, and static tunables for stall timeout and slow transfer rate.

Derived classes model protocol operations: `CurlOptionsOp` probes allowed verbs and resumes a parent operation; `CurlStatOp` implements HEAD/PROPFIND stat; `CurlOpenOp` adds file-open side effects; `CurlChecksumOp` reads checksum headers; `CurlDeleteOp` and `CurlMkcolOp` mutate objects; `CurlQueryOp` returns query buffers; `CurlReadOp`, `CurlPrefetchOpenOp`, and `CurlPgReadOp` implement normal reads and prefetch/page-read variants; `CurlVectorReadOp` implements multi-range reads; `CurlListdirOp` parses WebDAV listings; `CurlCopyOp` implements third-party copy over HTTP COPY; `CurlPutOp` streams uploads with pause/continue support.

## Control flow

The header establishes the worker contract: operations are queued, configured with curl handles by `CurlWorker`, optionally paused/continued through `HandlerQueue`, and completed by invoking a response handler exactly once. Operations needing endpoint capability discovery return `RequiresOptions()`, causing the worker to execute a `CurlOptionsOp` before the original operation. Redirects return `Fail`, `Reinvoke`, or `ReinvokeAfterAllow` so the worker can restart immediately or probe allowed verbs at the new endpoint.

## State and persistence behavior

State is per-operation and in-memory. `CurlOperation` owns the easy handle while running, header parser, response-info object, curl header list, timeout and transfer counters, broker callout object, fake DNS curl resolve list, and handler pointer. Derived classes add operation-specific buffers and references to caller-owned buffers or file objects. No class in this header persists data to disk.

## Dependencies and integration points

The header depends on local connection/header callout APIs, response-info APIs, checksum utilities, XRootD buffer/response types, `curl/curl.h`, and the worker/queue abstractions. It is the main integration surface between `XrdClHttpFile`, `XrdClHttpFilesystem`, `XrdClHttpFactory`, and the operation implementation files.

## Risks and edge cases

Most classes own or reference resources with different lifetimes: handler pointers, caller buffers, curl handles, `File` objects, shared queues, and response-info wrappers. New operation implementations must release curl options for handle recycling and must not call handler callbacks twice. Derived classes that pause transfers must handle race conditions where a worker has already failed an operation before a continuation arrives.

## Test signals

The public methods intended for tests include vector-read separator/status injection, static timeout/rate setters, monitoring JSON, and factory/header timeout paths. Compile-time coverage through all operation `.cc` files is important because this header coordinates many cross-file virtual methods.
