# sources/distributed-fs/xrootd/src/XrdCl/XrdClLocalFileTask.cc

## Purpose

This file implements the small job object used to deliver completed local-file results through the XrdCl job manager. It decouples local filesystem completion from user callback execution.

## Important APIs, Types, And Functions

`LocalFileTask::LocalFileTask` stores pointers to `XRootDStatus`, `AnyObject`, `HostList`, and `ResponseHandler`. `Run(void*)` invokes `responsehandler->HandleResponseWithHosts(st, obj, hosts)` when a handler exists. If no handler exists it deletes the status, response, and host list itself. It then deletes `this`.

## Control Flow

`LocalFileHandler::QueueTask` or AIO completion creates a `LocalFileTask` and queues it to `JobManager`. When the job manager runs it, ownership of response data transfers to the response handler through `HandleResponseWithHosts`; otherwise the task cleans up. The task self-destructs at the end of `Run`.

## State And Persistence

The task only stores transient heap pointers until execution. It has no persistent state and performs no filesystem mutation. Its persistence impact is indirect: it determines whether local operation results are delivered or deallocated.

## Dependencies And Integration Points

It depends on `XrdClLocalFileTask.hh`, `Job`, `ResponseHandler`, `HostList`, `XRootDStatus`, and `AnyObject`. It is queued by `LocalFileHandler` and executed by `JobManager`.

## Risks

The task assumes the response handler takes ownership of `st`, `obj`, and `hosts`. If a handler implementation does not delete or otherwise manage them, leaks result. `delete this` makes stack allocation or external ownership invalid, though current construction uses `new`. The unused `arg` parameter confirms this job is not context-driven.

## Test Signals

Tests should verify callback invocation with host metadata, cleanup when handler is null, no double-delete when handlers consume responses, and that synchronous local operations queued through the job manager eventually execute exactly once.
