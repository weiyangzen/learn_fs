# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.cc

## Purpose

`XrdOfsTPCJob.cc` implements queued/running/done destination-side TPC copy jobs. It bridges OFS write-open/sync semantics to a bounded pool of external transfer-program workers.

## Important APIs, Types, and Functions

Implemented methods are constructor, `Del`, `Done`, and `Sync`. Static state is `jobMutex`, FIFO head `jobQ`, and tail `jobLast`. Each job stores `Next`, assigned `XrdOfsTPCProg *myProg`, completion `eCode`, `Status`, and optional source-LFN rename positions `lfnPos`.

## Control Flow

`Sync()` is the main entry. If already running, it installs a callback and returns `SFS_STARTED`. If done, it returns success or stored error. If waiting, it tries `XrdOfsTPCProg::Start`; on no worker, it enqueues itself and returns `SFS_STARTED`; on thread creation error, it records a terminal resource failure. `Done()` marks a running job complete, replies to any waiter, pulls the next queued job if present, attaches the freed program to it, and returns that next job to the runner loop. `Del()` removes queued jobs or cancels running jobs and notifies premature-close callbacks.

## State and Persistence Behavior

Jobs live on the heap and are reference-counted with the inherited `Refs`. The queue is process-memory only, serialized by `jobMutex`. Completion text is stored in `Info.Key` when a job fails, reusing the field that previously held the source URL. No copy state persists after object deletion except files created by the transfer, with optional cleanup through `autoRM`.

## Dependencies and Integration Points

The job layer uses `XrdOfsTPCProg` for execution, `XrdOucCallBack` for wait-response behavior, `XrdSfsInterface` return codes, `OfsEroute` logging, and `XrdOfsStats` indirectly through `Info.Fail`.

## Risks and Edge Cases

`Info.Key` changes meaning from source URL to error text after completion, which is compact but easy to misuse. Callback replies intentionally unlock `jobMutex`; lifetime/ref accounting around that path is critical. Queue fairness is FIFO, but only worker completion starts queued jobs.

## Test Signals

Tests should cover immediate start, queued start, running async wait, done success, done failure, cancellation via close, resource failure from thread creation, and FIFO handoff when multiple jobs wait.
