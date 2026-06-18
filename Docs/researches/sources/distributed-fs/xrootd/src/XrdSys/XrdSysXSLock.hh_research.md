# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.hh

Purpose: declares the legacy shared/exclusive lock class and its usage enum.

Important APIs/types/functions: `XrdSysXS_Type` values are `xs_None`, `xs_Shared`, and `xs_Exclusive`. `XrdSysXSLock` exposes `Lock()` and `UnLock()`, and stores mode/count/waiter state plus mutex and semaphore wait channels.

Control flow: callers request either shared or exclusive access, then unlock with either the matching type or `xs_None` to skip mode validation. Multiple shared holders are allowed; one exclusive holder is allowed; upgrades and downgrades are unsupported.

State and persistence: object-local counters and wait queues represent all state. No static state or OS rwlock is used.

Dependencies and integration: includes `XrdSysPthread.hh` for mutex/semaphore abstractions. It is a compatibility synchronization primitive for older XRootD code.

Risks: no RAII helper is provided in this header, so exception paths can leak locks. `UnLock(xs_None)` weakens misuse detection. Destruction with waiters aborts the process.

Test signals: API-level lock/unlock cycles, shared compatibility, exclusive exclusion, and negative misuse tests.
