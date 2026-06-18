# sources/test-tools/stress-ng/stress-mutex.c

Purpose: implements `mutex`, a pthread mutex/scheduler stressor. It creates multiple contending pthreads that repeatedly change scheduling priority, optionally move CPU affinity, lock/unlock a shared mutex, and measure lock latency.

Important APIs/types/functions: global `pthread_mutex_t mutex` is the contended lock. `pthread_info_t` stores priority limits, affinity setting, pthread handle, creation status, and metrics. Optional mutex attributes set `PTHREAD_PRIO_INHERIT` and a priority ceiling. `stress_mutex_exercise()` performs per-thread priority/affinity changes and lock/unlock; `stress_mutex()` handles option parsing, mutex initialization, CPU list setup, thread lifecycle, and metrics.

Control flow: setup installs SIGCHLD handling, reads `mutex-procs` and `mutex-affinity`, obtains SCHED_FIFO priority range, initializes the mutex with priority inheritance when supported, and optionally collects allowed CPUs. After synchronization it creates the requested pthreads. Each thread reseeds, sleeps briefly, repeatedly chooses a FIFO priority, calls `pthread_setschedparam()`, times occasional mutex lock calls, drops priority, optionally changes affinity, yields, increments bogo, and unlocks. On stop, the parent joins threads, destroys the mutex, frees CPU lists, and reports nanoseconds per mutex.

State and persistence: state is in-process pthread/mutex state plus optional CPU list memory. No filesystem or IPC state persists.

Dependencies and integration: requires POSIX priority scheduling, pthread mutex APIs, `pthread_setschedparam`, SCHED_FIFO priority queries, and optional pthread affinity. Uses stress-ng affinity helpers, signal helpers, settings, timing, and metrics.

Risks and test signals: real-time scheduling calls may fail without privileges but are intentionally ignored unless mutex operations fail. Affinity support is nonportable. Signals are successful thread creation, no lock/unlock failures, bogo increments, nanoseconds-per-mutex metrics, and unimplemented status on platforms without required pthread/scheduler support.
