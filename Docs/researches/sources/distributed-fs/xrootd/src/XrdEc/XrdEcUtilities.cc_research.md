# sources/distributed-fs/xrootd/src/XrdEc/XrdEcUtilities.cc

## Purpose

This source implements XrdEc callback scheduling helpers. It converts immediate status or read-chunk data into XrdCl `Job` instances queued on the default postmaster job manager, preserving asynchronous callback behavior even when the operation completes locally.

## Important APIs, Types, and Functions

`ResponseJob` derives from `XrdCl::Job` and owns a `ResponseHandler*`, heap-allocated `XRootDStatus*`, and optional `AnyObject*`. Its `Run()` calls `HandleResponse()` and deletes the job object.

`ScheduleHandler(uint64_t offset, uint32_t size, void *buffer, ResponseHandler*)` creates a `ChunkInfo`, wraps it in `AnyObject`, and queues a successful response. `ScheduleHandler(ResponseHandler*, const XRootDStatus&)` queues a status-only response.

## Control Flow

Both helpers return immediately when the handler is null. Otherwise they allocate response payloads and queue a `ResponseJob` through `XrdCl::DefaultEnv::GetPostMaster()->GetJobManager()->QueueJob(job)`. XrdCl later invokes the job and the user handler receives ownership according to normal XrdCl callback conventions.

## State and Persistence Behavior

The file has no persistent state. Its only state is temporary heap allocation for status, response objects, chunk metadata, and scheduled jobs.

## Dependencies and Integration Points

The implementation depends on `XrdClJobManager`, `XrdClPostMaster`, and `XrdClDefaultEnv`. It integrates with XrdEc read/write code paths that need to deliver callbacks through the same asynchronous machinery as network operations.

## Risks and Edge Cases

The code assumes `HandleResponse()` or XrdCl response ownership will dispose of `pStatus` and `pResponse`; `ResponseJob` deletes only itself. If callback ownership differs, this leaks. The raw `buffer` pointer in `ChunkInfo` must remain valid under XrdCl's expected callback lifetime. There is no failure path if the default postmaster or job manager is unavailable.

## Test Signals

Tests should verify null-handler no-ops, status propagation, chunk offset/length/buffer propagation, callback execution on the postmaster queue, and memory ownership under sanitizers.
