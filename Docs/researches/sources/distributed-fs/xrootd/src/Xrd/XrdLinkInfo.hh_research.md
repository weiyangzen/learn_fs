## sources/distributed-fs/xrootd/src/Xrd/XrdLinkInfo.hh

Purpose: defines the small mutable state bundle used to coordinate link closure, serialization, error reporting, and per-link lifecycle fields.

Important APIs/types/functions: `XrdLinkInfo` contains `KillcvP`, `IOSemaphore`, `conTime`, `Etext`, recursive `opMutex`, `InUse`, `doPost`, `FD`, and `KillCnt`. `Reset()` initializes connection time, clears error text, sets `InUse` to one, clears waiters, and marks the fd invalid.

Control flow: `XrdLinkXeq::Reset()` calls `LinkInfo.Reset()` for reused objects. `XrdLink::Serialize()`, `setRef()`, `Terminate()`, and `XrdLinkXeq::Close()` coordinate through `opMutex`, `InUse`, `doPost`, `IOSemaphore`, and `KillcvP`.

State/persistence: memory-only connection state. `Etext` is heap-owned and freed on reset or close. `conTime` is sampled with `time(0)` and later contributes to aggregate connection-time stats.

Dependencies/integration: depends on `XrdSysCondVar`, `XrdSysSemaphore`, and `XrdSysRecMutex`.

Risks: `KillcvP` is protected by `opMutex`, but the pointed condvar has its own lock ordering requirements. Misordered locking can deadlock termination. `KillCnt` is a `char`; masking in `XrdLink.cc` assumes narrow counter semantics.

Test signals: verify reset frees prior `Etext`, close signals `KillcvP`, serialization posts `IOSemaphore`, and connection duration is reflected in stats on close.
