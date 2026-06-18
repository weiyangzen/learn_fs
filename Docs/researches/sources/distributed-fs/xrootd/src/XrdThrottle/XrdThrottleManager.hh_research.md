# sources/distributed-fs/xrootd/src/XrdThrottle/XrdThrottleManager.hh

Purpose: Declares the XrdThrottleManager service and its XrdThrottleTimer RAII helper. The manager enforces global and per-user throttles for bytes, operations, active I/O concurrency, open files, and connections while trying to preserve user fair share through hash-bucketed user IDs.

Important APIs/types/functions: Public configuration and enforcement entry points are Init(), FromConfig(), SetThrottles(), SetLoadShed(), SetMaxOpen(), SetMaxConns(), SetMaxWait(), LoadUserLimits(), ReloadUserLimits(), GetUserMaxConn(), OpenFile(), CloseFile(), Apply(), StartIOTimer(), PrepLoadShed(), CheckLoadShed(), and PerformLoadShed(). GetUserInfo() derives a username and uint16_t bucket. The Waiter struct owns per-user condition variables and EWMA accounting. XrdThrottleTimer starts timing in its constructor, links itself into a hashed TimerList, and calls StopIOTimer() from its destructor.

Control flow: Callers identify the user, call Apply() or StartIOTimer(), block behind Waiter::Wait() when shares or concurrency are exhausted, and rely on a recompute thread to refill shares and compute wake order. RecomputeInternal(), ComputeWaiterOrder(), UserIOAccounting(), NotifyOne(), GetShares(), and StealShares() are private implementation hooks declared here.

State/persistence: State is in memory: fixed-size share vectors, waiter arrays, relaxed atomics, open/connection maps, active-connection maps keyed by pid, per-user limit map, and reloadable config filename. No durable persistence is declared beyond reading user-limit configuration.

Dependencies/integration: Uses XrdSys atomics, condition variables, pthread bootstrap, XrdSecEntity, XrdOucTrace, XrdSysError, XrdXrootdGStream monitoring, and XrdThrottle::Configuration.

Risks: UID hashing can collide, so limits/fairness are approximate. The mix of relaxed atomics, std::mutex, XrdSysCondVar, and shared_mutex demands careful implementation. TimerList link/unlink correctness is critical because timer destructors mutate linked lists. User-limit wildcard semantics are only declared here and need implementation tests.

Test signals: Exercise throttle refill fairness, hashed-user collision behavior, max wait timeout, max open/max connection counters including pid cleanup, user-limit reload while readers call GetUserMaxConn(), load-shed opaque handling, and RAII timer cleanup under exceptions.
