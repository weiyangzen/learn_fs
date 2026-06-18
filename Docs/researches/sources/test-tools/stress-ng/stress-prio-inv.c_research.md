# sources/test-tools/stress-ng/stress-prio-inv.c research

Purpose: implements the `prio-inv` stressor, a scheduler and pthread mutex test that creates three cooperating child processes to exercise priority inversion behavior under selectable scheduler policies and pthread mutex protocols.

Important APIs, types, and functions: the file defines option tables for `prio-inv-policy` and `prio-inv-type`, maps unavailable platform constants to negative sentinels, and exposes `stress_prio_inv_info`. Core state lives in a shared anonymous `stress_prio_inv_info_t` containing child accounting and a process-shared `pthread_mutex_t`. `stress_prio_inv_set_prio_policy()` wraps `sched_setscheduler()` and `setpriority()`, falling back from realtime policies to `SCHED_OTHER` on `EPERM`. `mutex_exercise()` locks/unlocks the shared mutex and increments bogo ops; `cpu_exercise()` samples user CPU time without taking the mutex.

Control flow: `stress_prio_inv()` mmaps shared state, resolves settings, validates unsupported/non-root policies, initializes a robust mutex with the requested protocol and priority ceiling, then forks three children. Child 0 and 2 contend on the mutex while child 1 burns CPU. The parent raises its own priority, waits for stress termination, signals all children with `SIGALRM`, waits for them, destroys pthread state, and compares runtime usage to warn about ineffective priority inheritance.

State and persistence: only transient anonymous shared memory and child processes are used; no files persist. Global `t_end` bounds child loops by the stress timeout.

Dependencies and integration: gated by POSIX priority scheduling, pthread mutex attribute APIs, `sched_*`, `setpriority`, and stress-ng helpers for settings, sync, signals, capabilities, and metrics. Integrated through stressor metadata with `CLASS_OS | CLASS_SCHEDULER` and `VERIFY_ALWAYS`.

Risks: realtime policy requests need privilege, robust/protocol attributes may be ignored or unsupported, and the code returns early in a few setup error paths without sharing the common unmap cleanup. Runtime comparison is heuristic and can be noisy on loaded systems.

Test signals: build-time unimplemented path, option parsing for all policy/type values, non-root fallback messages, child reap behavior, bogo increments, and the priority-inheritance warning are the main observable signals.
