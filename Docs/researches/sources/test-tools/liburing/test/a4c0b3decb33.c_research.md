<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/a4c0b3decb33.c -->
## sources/test-tools/liburing/test/a4c0b3decb33.c

Purpose: syzkaller-generated regression with process supervision and raw io_uring interactions.

Important APIs/types/functions: includes time helpers, environment/setup helpers, `kill_and_wait`, `setup_test`, `loop`, and `execute_one`. The sanitizer build provides an alternate skip `main`.

Control flow: non-sanitizer execution sets up the test environment, repeatedly forks/runs the reproduced sequence, kills timed-out children, and exits on interrupt or completion. `execute_one` performs the minimized syscall/liburing calls.

State and persistence behavior: temporary child processes, descriptors, and any kernel ring state are cleaned by process exit and supervisor kill paths. Environment setup may write to proc/sysfs/cgroup locations.

Dependencies and integration points: uses pthread/syscall/process APIs, `liburing.h`, `helpers.h`, and raw syscall conventions.

Risks: generated supervisor code can be timing-sensitive and platform-sensitive. The reproducer is intentionally narrow, so changes to syscall return values across kernels may require skip handling.

Test signals: pass or controlled skip means the original crash/hang reproducer is no longer active in the tested environment.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/a4c0b3decb33.c -->
