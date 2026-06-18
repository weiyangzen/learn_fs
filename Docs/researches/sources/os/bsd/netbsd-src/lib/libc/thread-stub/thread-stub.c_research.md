# File Research: sources/os/bsd/netbsd-src/lib/libc/thread-stub/thread-stub.c

## Purpose
Implements libc thread-operation stubs for programs not linked with libpthread.

## Key Elements
Provides weak aliases for pthread join/detach, mutexes, mutex attributes, condition variables, rwlocks, TSD operations, once, signal mask, self, yield, create, exit, cancel state, equality, and current CPU. Most lock operations are no-ops while `__isthreaded == 0`; many abort via `SIGABRT` if used after threading is active.

## Dependencies
Uses `_REENTRANT`, `reentrant.h`, `tsd.h`, `namespace.h`, `errno`, `signal`, `stdlib`, `unistd`, `sigprocmask`, `exit`, and `_sys_sched_yield`.

## Behavior/Risks
Provides real single-thread TSD storage via `__libc_tsd`; destructors are stored but not run, and deleted keys are not recycled. `pthread_create` returns `EOPNOTSUPP`, self returns `(thr_t)-1`, and `thr_exit` exits the process. Correctness depends on libpthread overriding these weak symbols in threaded programs.
