# sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.cpp

Purpose: Implements a small synchronous periodic task wrapper used by the legacy C++ cache to call purge functions on a `LoopThread`.

Important APIs and types: `PeriodicTask::PeriodicTask(function<void()>, double intervalSec, string threadName)` and private `_loopIteration` are implemented here. It uses `cpputils::LoopThread` and Boost chrono sleep.

Control flow: The constructor converts the interval seconds to nanoseconds, constructs a loop thread bound to `_loopIteration`, and starts it. Each loop iteration sleeps interruptibly for the interval, invokes the task, and returns true to continue running.

State and persistence behavior: State is the task callback, interval, and background thread. Persistence effects depend on the callback, typically cache eviction and block flush.

Dependencies and integration points: Used by `Cache` to run `_deleteOldEntriesParallel` every purge interval. Depends on cpp-utils logging/thread support and Boost thread sleep because the sleep must be interruptible by `LoopThread`.

Risks: Callback exceptions are not caught here. Lifetime depends on `_thread` being last in the header so it is destroyed first; otherwise a running thread could access destroyed callback/interval state. The first task run occurs only after sleeping.

Test signals: No direct tests in this subset. Cache timeout behavior and thread shutdown are the implied validation points.

Source-read signal: Read `sources/security-integrity/cryfs/old-cpp/src/blockstore/implementations/caching/cache/PeriodicTask.cpp` completely for this pass (26 lines, 827 bytes).
