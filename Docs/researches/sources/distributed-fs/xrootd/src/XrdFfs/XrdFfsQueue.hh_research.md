# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsQueue.hh

## Purpose

This header declares the C ABI and task structure for the XrdFfs pthread work queue.

## Important APIs, Types, and Functions

`struct XrdFfsQueueTasks` stores mutex, condition variable, done state, function pointer, argument pointer, id, and linked-list pointers. Public functions create, wait for, free, and count tasks, plus create/remove/count workers.

## Control Flow

Callers submit tasks with a function pointer and argument pointer, wait for completion when needed, then free the task. The worker pool processes tasks asynchronously.

## State and Persistence Behavior

The header stores no state but exposes the task layout used by the source file's global queue.

## Dependencies and Integration Points

It includes pthreads and is consumed by `XrdFfsMisc.cc`, `XrdFfsPosix.cc`, and `XrdFfsXrootdfs.cc`.

## Risks and Edge Cases

The function pointer signature uses `void **args`, while several callers cast addresses through `void**`; this is type-unsafe and can hide ABI mistakes. No include guard is present.

## Test Signals

Compile tests should catch strict-pointer warnings. Runtime tests should validate create/wait/free ownership and worker lifecycle.
