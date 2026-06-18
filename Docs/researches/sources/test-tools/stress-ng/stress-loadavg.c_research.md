# sources/test-tools/stress-ng/stress-loadavg.c

Purpose: implements `loadavg`, a pthread fan-out stressor that creates many low-priority threads to raise scheduler load average, with optional Linux temp-file I/O to contribute blocked I/O load.

Important APIs/types/functions: `stress_loadavg_info_t` records thread handles and creation status. Volatile flags `keep_running_flag` and `keep_thread_running_flag` coordinate shutdown. `stress_loadavg_threads_max()` reads `/proc/sys/kernel/threads-max`. `stress_loadavg_func()` is the per-thread loop.

Control flow: the worker resolves `loadavg-max`, caps it to `threads-max` when known, divides per stress-ng instance, allocates thread records, optionally creates an unlinked temp file for Linux I/O, blocks SIGALRM and polls pending signals, sync-starts, then creates up to the per-worker thread limit. Threads nice themselves to 19, optionally seek/write one byte to the temp fd, increment bogo ops, yield, and stop on time or flags. The parent sleeps/yields until stop, clears the thread flag, joins created threads, closes/removes resources, and exits.

State and persistence behavior: runtime state is thread records, shared stop flags, optional temp fd, and process signal mask. The temp file is unlinked immediately and temp directory removed after close.

Dependencies and integration points: compile-gated on pthread support. Uses stress-ng pthread args, signal pending helper, temp filesystem helpers, settings, bogo ops, and process state. Registered as `CLASS_SCHEDULER | CLASS_OS`.

Risks: extremely high thread counts can exhaust process or system resources, so creation stops on `EAGAIN`. Blocking SIGALRM changes signal handling assumptions within the process. On Linux all threads share a single temp fd for optional writes.

Test signals: run min, default, and capped high `--loadavg-max`, check graceful handling of `EAGAIN`, all created threads joined, temp dir removed, and bogo ops from worker threads.
