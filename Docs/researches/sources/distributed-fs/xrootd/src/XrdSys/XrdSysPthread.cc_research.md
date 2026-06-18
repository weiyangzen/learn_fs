# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPthread.cc

Purpose: implements the non-inline portions of XRootD's pthread abstraction: condition-variable timed waits, Apple/GNU semaphore fallback behavior, thread creation helpers, thread numeric IDs, stack sizing, joins, and recursive mutex initialization.

Important APIs/types/functions: `XrdSysThread_Xeq()` is the extern C trampoline. `XrdSysCondVar::Wait()`, `WaitMS()`, and `XrdSysCondVar2::WaitMS()` wrap pthread condition waits. Apple/GNU `XrdSysSemaphore` methods implement a counting semaphore with `XrdSysCondVar`. `XrdSysThread::Run()`, `Num()`, `setStackSize()`, and `Wait()` provide process-wide thread utilities. `XrdSysRecMutex::{InitRecMutex,ReInitRecMutex}` build recursive mutexes.

Control flow: `Run()` allocates `XrdSysThreadArgs`, initializes attributes based on bind/detach/stack options, and launches `XrdSysThread_Xeq()`, which logs start messages, calls the user procedure, deletes the args, and returns the procedure result. Timed waits calculate an absolute `timespec`, retry on `EINTR`, and report timeout as true. The fallback semaphore uses a condition variable, `semVal`, and `semWait` to block or post waiters.

State and persistence: static `XrdSysThread::eDest` controls debug logging and `stackSize` affects future thread creation. Condition variables, semaphores, and mutexes store pthread handles in object state.

Dependencies and integration: wraps pthreads, semaphores, `gettimeofday`, platform-specific thread IDs (`SYS_gettid`, `pthread_mach_thread_np`), and Windows sleep/time headers where needed. This file underpins many XrdSys classes and XrdThrottle's recompute thread.

Risks: `Run()` leaks `XrdSysThreadArgs` if `pthread_create()` fails. `XrdSysThread::Wait()` assumes the joined thread returned an `int *` and dereferences it, which is only safe for legacy callers following that convention. Timed waits use wall-clock time, so clock jumps affect timeout behavior. `InitRecMutex()` destroys `cs` during construction before it has necessarily been initialized by the base constructor path.

Test signals: tests should cover detached and joinable thread creation, stack size forcing/default suppression, timed wait timeout and signal paths, semaphore post/wait fairness, and recursive mutex reinitialization.
