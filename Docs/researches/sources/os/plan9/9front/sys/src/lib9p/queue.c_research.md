# File Research: sources/os/plan9/9front/sys/src/lib9p/queue.c

## Read Status
Complete: 104 lines read.

## Purpose
Implements a request queue with a worker proc for serializing potentially interruptible request handlers.

## Main Responsibilities
- Create a queue backed by a Plan 9 proc.
- Push requests with handler callbacks.
- Remove or interrupt queued/current requests on flush.
- Shut down the queue by pushing a sentinel request.

## Important Functions
- `reqqueuecreate`: allocates queue and starts `_reqqueueproc`.
- `reqqueuepush`: appends a request and wakes the worker.
- `reqqueueflush`: interrupts the current request or removes a queued request and responds `"interrupted"`.
- `reqqueuefree`: sends a nil-handler sentinel to terminate the worker.
- `_reqqueueproc`: worker loop that pops requests and runs callbacks.

## Dependencies and Interactions
- Uses `proccreate`, `threadint`, `rsleep`, `rwakeup`, `QLock`.
- Writes `nointerrupt` to `/proc/<pid>/ctl` before waiting to avoid interruption while idle.
- The queue node is embedded in `Req` as `r->qu`.
