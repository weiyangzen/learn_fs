# sources/distributed-fs/xrootd/src/XrdSys/XrdSysSemWait.hh

Purpose: implements a simple counting semaphore with a timed wait primitive using `XrdSysCondVar`.

Important APIs/types/functions: `CondWait()`, `Post()`, blocking `Wait()`, timed `Wait(int secs)`, constructor with initial value and condition ID, and private `semVal`/`semWait` counters.

Control flow: `CondWait()` takes the condition mutex, decrements `semVal` if positive, otherwise returns would-block. `Wait()` decrements immediately when possible or increments `semWait` and waits on the condition variable. `Wait(secs)` is the timed version and decrements `semWait` on timeout. `Post()` signals a waiter if `semWait > 0`; otherwise it increments the available count.

State and persistence: the semaphore count and waiting count live in the object and are protected by `semVar`'s mutex. There is no kernel semaphore or cross-process state.

Dependencies and integration: depends on `XrdSysPthread.hh` for `XrdSysCondVar`. It is a lightweight in-process primitive used where timed semaphore behavior is needed independent of platform semaphore APIs.

Risks: `Wait()` uses an `if` rather than a loop around the condition wait, so spurious wakeups can consume a nonexistent post. `Post()` decrements `semWait` before the waiter has necessarily resumed, which makes accounting sensitive to races and cancellation. Fairness is explicitly not guaranteed.

Test signals: exercise immediate acquire, timeout, post-before-wait, post-after-wait, multiple waiters, and spurious wakeup/cancellation behavior if the platform can inject it.
