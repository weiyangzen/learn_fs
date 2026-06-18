# sources/test-tools/stress-ng/stress-longjmp.c

Purpose: implements `longjmp`, a CPU/hot stressor for `setjmp()`/`longjmp()` behavior. It repeatedly jumps out of leaf functions and checks that the saved jump buffer is not corrupting adjacent memory.

Important APIs/types/functions: `jmp_buf_check_t` wraps a timestamp, canary before the `jmp_buf`, the `jmp_buf`, and a canary after it. `stress_longjmp_sample_func()` records a timestamp then longjmps; `stress_longjmp_func()` longjmps without timing. `stress_longjmp()` runs the setjmp loop, validates canaries, tracks sampled timing, and registers metrics.

Control flow: after synchronization, `setjmp()` establishes the return point. The first jump in each 1000-call sample period records timing and increments bogo operations; intervening jumps reduce timing overhead. The loop continues by calling one of the no-return jump functions until the stop condition is false.

State and persistence: static state includes canaries, total sampled time, sample count, and `sample_counter`. There is no external state. The metric is nanoseconds per sampled longjmp call.

Dependencies/integration: relies on standard `jmp_buf`, stress-ng timing, bogo counters, proc-state synchronization, and `VERIFY_ALWAYS`. Functions are marked `NOINLINE`, `NORETURN`, and low optimization to preserve call shape.

Risks/test signals: this is sensitive to ABI/compiler behavior around nonlocal jumps. Useful signals are bogo increments, timing metrics, no canary corruption failures, and no path reaching post-`longjmp()` `_exit()` guards.
