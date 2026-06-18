# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gp_wsync.c

Purpose: Implements Win32 synchronization and threading primitives behind the portable `gpsync.h` interface.

Key interfaces: `gp_semaphore_sizeof/open/close/wait/signal`, `gp_monitor_sizeof/open/close/enter/leave`, and `gp_create_thread`.

Control flow: semaphores wrap `CreateSemaphore`, `WaitForSingleObject`, `ReleaseSemaphore`, and `CloseHandle`. Monitors wrap `CRITICAL_SECTION`. Thread creation allocates a closure, starts a wrapper with `BEGIN_THREAD`, invokes the callback, frees the closure in the thread, and terminates with `_endthread`.

Dependencies: Uses Windows synchronization APIs, `<process.h>`, Ghostscript error codes, `gpsync.h`, and `windows_.h` for compiler-specific `BEGIN_THREAD`.

Risks and notes: `gp_monitor_open(NULL)` reports monitors as fixed because critical sections must not move. A thread-start failure leaks the closure because it is freed only by the wrapper. The semaphore maximum uses `max_int`.
