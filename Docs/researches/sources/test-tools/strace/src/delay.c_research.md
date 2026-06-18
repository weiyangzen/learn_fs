<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/delay.c -->
## sources/test-tools/strace/src/delay.c

Purpose: Implements syscall delay injection storage and timer management.

Important APIs and types: `struct inject_delay_data`, globals `delay_data_vec`, capacity/size counters, `delay_timer`, `delay_timer_is_armed`, and functions `alloc_delay_data`, `fill_delay_data`, `is_delay_timer_armed`, `delay_timer_expired`, `arm_delay_timer`, `delay_tcb`.

Control flow: Delay specs are allocated in a growable vector. `fill_delay_data` stores enter or exit delay durations. `delay_tcb` marks a tracee delayed/tampered, computes absolute expiration from `CLOCK_MONOTONIC`, creates the POSIX timer on first use, compares against the currently armed timer, and arms the timer for the chosen tracee.

State and persistence: Process-global vector stores configured delays. A single process-global POSIX timer and boolean track active delay wakeups. Each delayed `tcb` stores its own absolute expiration time and flags.

Dependencies and integration: Depends on `defs.h`, `delay.h`, timespec helpers, `xgrowarray`, `timer_create`, `timer_settime`, and tracing-loop handling of `TCB_DELAYED`.

Risks: Timer comparison uses the selected delay interval rather than the stored absolute expiration, so changes here need careful review. Delay index overflow is fatal. A single timer must serve all delayed tracees correctly.

Test signals: Tests should cover enter and exit delays, multiple configured delay indices, timer re-arming order, invalid index death paths, and interaction with injected syscall tampering flags.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/delay.c -->
