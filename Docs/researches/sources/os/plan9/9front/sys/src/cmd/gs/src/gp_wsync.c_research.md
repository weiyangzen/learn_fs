# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gp_wsync.c

Purpose: Win32 synchronization and thread primitive implementation for Ghostscript.

Semaphores: Wraps `CreateSemaphore`, `CloseHandle`, `WaitForSingleObject`, and `ReleaseSemaphore`. `gp_semaphore_open(NULL)` reports that semaphore storage may be moved.

Monitors: Wraps Win32 `CRITICAL_SECTION` as `gp_monitor`. `gp_monitor_open(NULL)` reports that monitor storage must not be moved because critical sections are address-sensitive.

Threads: `gp_create_thread` allocates a small closure containing callback and data, starts `gp_thread_begin_wrapper` via `BEGIN_THREAD`, frees the closure in the new thread, invokes the callback, and calls `_endthread`.

Dependencies and notes: Uses `gpsync.h`, Ghostscript error codes, `windows_.h`, and `<process.h>`. Failure reporting maps Windows API failures to Ghostscript VM or unknown errors.
