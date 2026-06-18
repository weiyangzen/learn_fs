# sources/distributed-fs/xrootd/src/XrdSys/XrdSysXSLock.cc

Purpose: implements a custom shared/exclusive lock with semaphore-based wait queues and anti-starvation toggling.

Important APIs/types/functions: `XrdSysXSLock::~XrdSysXSLock()`, `Lock(XrdSysXS_Type)`, and `UnLock(XrdSysXS_Type)` implement the behavior declared in the header.

Control flow: `Lock()` serializes on `LockContext`; shared lock requests can join existing shared holders only when no exclusive waiter exists, otherwise wait on `WantShr`; exclusive requests wait on `WantExc` until `cur_count` reaches zero. `UnLock()` validates state and optional usage, decrements `cur_count`, then wakes either one exclusive waiter or all shared waiters based on `exc_wait`, `shr_wait`, and `toggle`.

State and persistence: mutable state includes current mode/count, exclusive/shared waiter counts, a toggle bit, a mutex, and two semaphores. No state persists outside the object.

Dependencies and integration: uses `XrdSysHeaders.hh`, `XrdSysXSLock.hh`, `XrdSysMutex`, and `XrdSysSemaphore`. It predates the standard/shared pthread rwlock wrapper and may be used by legacy code needing explicit fairness behavior.

Risks: destructor aborts if destroyed while active or with waiters. Unlock misuse throws string literals after writing to `std::cerr`. The waiting counts are decremented by the unlocker before the waiter resumes, so cancellation or unexpected wakeups can corrupt accounting. No upgrade/downgrade support exists.

Test signals: multiple readers, writer exclusion, writer preference once waiting, alternating reader/writer fairness, invalid unlock mode, unlock inactive lock, and destruction while idle only.
