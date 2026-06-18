# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCProg.hh

## Purpose

`XrdOfsTPCProg.hh` declares the worker object that runs an external TPC transfer program for `XrdOfsTPCJob` instances.

## Important APIs, Types, and Functions

Public methods are `Cancel`, static `Init`, `Run`, static `Start`, `Xeq`, constructor, and destructor. Private state includes `ExportCreds`, global idle-list mutex/head, `XrdOucProg Prog`, `XrdOucStream JobStream`, list `Next`, current `Job`, prefix name `Pname`, and error buffer `eRec`.

## Control Flow

The class lifecycle is pool-based: `Init()` creates workers, `Start()` assigns one job and starts a thread, `Run()` executes jobs and recycles the worker, `Cancel()` drains the process stream.

## State and Persistence Behavior

Workers are persistent process-memory pool entries. Per-transfer state is current `Job`, process stream, and error record. No durable persistence is owned by the header contract.

## Dependencies and Integration Points

It includes `XrdOucProg`, `XrdOucStream`, and `XrdSysPthread`, and forward-declares `XrdOfsTPCJob`. It is used exclusively by the TPC job runner implementation and job queue.

## Risks and Edge Cases

Because one object is reused across transfers, `Run()` and `Xeq()` must reset enough per-job state. `Cancel()` only drains the stream; process termination semantics depend on `XrdOucStream`/`XrdOucProg`.

## Test Signals

Compile tests should include the header alongside `XrdOfsTPCJob`. Runtime tests should inspect reuse after success and failure, cancellation, and preservation of error text boundaries.
