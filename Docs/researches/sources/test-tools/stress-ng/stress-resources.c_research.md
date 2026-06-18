# sources/test-tools/stress-ng/stress-resources.c

Purpose: implements the `resources` stressor, which repeatedly forks children that allocate, access, and free many kinds of system resources through the shared `core-resources` helpers.

Important APIs/types/functions: `stress_resources_info` exposes `resources-mlock`, `resources-num`, and `resources-procs`. `stress_resources_alarm()` sends SIGALRM to all tracked child PIDs. `stress_resources()` drives process fan-out and calls `stress_resources_allocate()`, `stress_resources_access()`, and `stress_resources_free()`.

Control flow: the stressor resolves resource count and child count from settings/minimize/maximize flags, computes a free-memory floor, optionally enables `MCL_FUTURE`, maps a shared PID table, allocates the resource descriptor array, and synchronizes. Each loop initializes PID tracking, forks children until process count or memory floor is hit, and each child drops capabilities, applies scheduler settings, allocates resources, yields/accesses them, frees them, and exits. The parent reaps all forked children, sending SIGALRM and reporting slow cleanup when stopping.

State and persistence: state is transient process trees, resource descriptors, allocated kernel resources owned by children, and a shared PID table. Cleanup frees the descriptor array and unmaps PID state. No repository or durable filesystem state remains.

Dependencies and integration points: integrates with `core-resources`, `core-capabilities`, `core-out-of-memory`, `core-signal`, memory-limit helpers, pipe-size discovery, OOM adjustment, scheduler settings, and stress-ng sync/bogo accounting.

Risks and test signals: intentionally pressures process, memory, pipe, fd, IPC, and lock limits, so ENOMEM/fork failures and slow cleanup are expected. Test signals are no leaked children/resources, bogo increments per fork attempt, graceful memory-floor throttling, and successful cleanup even after stop signals.
