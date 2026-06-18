# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.hh

## Purpose

This header declares `XrdXrootdProtocol`, the central protocol object for xroot client sessions. It combines `XrdProtocol`, callback-driven input, direct I/O/sendfile support, and SFS exchange-buffer support in one per-link state machine.

## Important APIs, types, and functions

Public entry points include `Configure()`, `Match()`, `Process()`, `Recycle()`, `Stats()`, `SendFile()`, `SetFD()`, `Claim()`, `Swap()`, `Reclaim()`, `VerifyStream()`, `getData()` overloads, and `DoIt()`. Private request handlers cover authentication, open/read/write/vector I/O, page read/write, prepare, query, metadata, redirection, TLS, and configuration directives. `XrdXrootd::gdCallBack` and `XrdXrootd::IOParms` define callback and I/O parameter contracts.

## Control flow

The object is driven by `XrdLink`: `Match()` binds a link, `Process()` reads and dispatches requests, handler methods update `Response` and state, and `Recycle()` returns the object to `ProtStack`. Callback methods resume partial network reads and page writes. Parallel stream state uses `Stream[]`, `PathID`, semaphores, and mutexes to coordinate subordinate paths.

## State and persistence behavior

Static members store process configuration, filesystem/security services, redirect policy, TLS requirements, async thresholds, stats, and global route tables. Instance members store the active link, file table, monitor context, client/security entity, request-signature buffers, async counters, get-data continuation state, page-write control, buffer sizing, stream binding, protocol caps, and current request/response objects.

## Dependencies and integration points

The header depends on XRootD core protocol/link abstractions, SFS direct I/O and XIO, security interfaces, monitoring, request-id and response helpers, and protocol wire definitions. Almost every `XrdXrootd` execution module includes this header.

## Risks and edge cases

The class has a very large mutable surface; invariants are distributed across many `.cc` files. Static configuration makes unit isolation difficult. Member-function pointers in `Resume` and `ResumePio` must only reference methods valid for the current state. The copy assignment operator is deleted, but the object still has manual `Assign()`/pooling patterns that require careful reset/cleanup.

## Test signals

Tests should focus on externally visible protocol behavior: login/auth gates, dispatch table coverage, async and sendfile thresholds, TLS policy enforcement, bound-stream behavior, cleanup idempotence, and stats counters. Static config parser tests are also important because many handlers depend on process-wide members.
