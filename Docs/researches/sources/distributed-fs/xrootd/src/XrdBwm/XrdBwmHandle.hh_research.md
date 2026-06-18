# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmHandle.hh

Purpose: declares the request handle abstraction connecting BWM file operations to the scheduling policy and optional logger.

Important APIs/types/functions: `HandleState` values `Idle`, `Scheduled`, `Dispatched`; public `Activate`, `Alloc`, `Dispatch`, `Name`, `Retire`, `setPolicy`; private static allocator/ref-table helpers; `XrdBwmPolicy::SchedParms Parms`; callback fields `ErrCB` and `ErrCBarg`; inner `theEICB` semaphore callback used to synchronize async handoff.

Control flow: file open allocates a handle in `Idle`; `fctl` calls `Activate`; dispatch thread calls static `Dispatch`; close/destructor calls `Retire`.

State and persistence: per-handle state tracks policy status, request parameters, queue/run times, size/time counters, and policy reference handle. Static state tracks the active policy/logger and free handles.

Dependencies and integration points: includes `XrdBwmPolicy.hh`, `XrdOucErrInfo`, and XRootD pthread wrappers. The callback design is tied to SFS async error information.

Risks: the handle carries raw pointers for string fields and external callback pointers, so ownership discipline is enforced only in implementation. `Name()` assumes `Parms.Lfn` is valid unless called on dummy/uninitialized handles.

Test signals: API lifecycle from allocation through activation and retirement, callback wait/post behavior, policy registration, and use with dummy handle.
