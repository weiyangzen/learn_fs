# sources/distributed-fs/xrootd/src/XrdEc/XrdEcThreadPool.hh

## Purpose

This header implements a singleton thread-pool adapter for XrdEc. It wraps `XrdCl::JobManager` and exposes a C++ future-based `Execute()` API so erasure-coding work and checksum work can be scheduled without exposing XrdCl job objects to callers.

## Important APIs, Types, and Functions

`ThreadPool::Instance()` returns the process-local singleton. `Execute(FUNC, ARGs...)` packages a callable and moveable arguments into an `AnyJob`, queues it on the `JobManager`, and returns `std::future<std::invoke_result_t<FUNC, ARGs...>>`.

The private `sequence`/`seq_gen` templates and `tuple_call()` helpers unpack argument tuples in pre-C++17 style. `AnyJob<FUNC, RET, ARGs...>` derives from `XrdCl::Job`, owns the callable, argument tuple, and promise, and deletes itself at the end of `Run()`.

## Control Flow

The singleton constructor creates `XrdCl::JobManager threadpool(64)`, initializes it, and starts it. `Execute()` allocates a self-owning job, obtains its future before queueing, and passes the job to `QueueJob()`. When an XrdCl worker invokes `Run()`, the job calls the stored function with moved tuple arguments, sets the promise, and deletes itself.

The destructor stops and finalizes the job manager when the singleton is destroyed during process shutdown.

## State and Persistence Behavior

State is in-memory only: one `JobManager` with 64 worker capacity and a collection of queued jobs managed by XrdCl. There is no durable state. Futures are the only result handles returned to callers.

## Dependencies and Integration Points

This adapter is used by `WrtBuff::Encode()` for per-stripe CRC calculation and by `StrmWriter::EnqueueBuff()` for whole-buffer encoding. It depends on XrdCl job manager semantics, including self-deleting `Job` objects.

## Risks and Edge Cases

If the callable throws, `AnyJob::Run()` never catches the exception and the promise may never be fulfilled. `std::promise<void>` is handled by a void overload, but all jobs still rely on successful `set_value()`. The pool size is hard-coded to 64, which may oversubscribe small deployments or underserve high-throughput erasure-coded streams.

## Test Signals

Tests should cover value-returning and void callables, moved-only arguments, concurrent submissions, exception behavior, and shutdown after outstanding work. Integration signals come from XrdEc write throughput and absence of stuck futures during close.
