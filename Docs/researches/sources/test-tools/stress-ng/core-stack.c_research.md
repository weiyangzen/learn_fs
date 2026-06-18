# sources/test-tools/stress-ng/core-stack.c

Purpose: provides stack direction detection, alternative signal stack setup/sizing, stack-smash callback behavior, and optional backtrace dumping.

Important APIs/types/functions: `stress_stack_direction`, `stress_stack_top`, `stress_stack_sigalt_no_check`, `stress_stack_sigalt`, `stress_stack_sigalt_disable`, `stress_stack_sigstksz`, `stress_stack_minsigstksz`, `stress_stack_smash_check_flag_set`, and `stress_stack_backtrace`. A weak `__stack_chk_fail` override is compiled for selected GCC/musl builds.

Control flow: stack direction compares addresses of caller/local variables through a noinline helper. `stress_stack_top` offsets from the supplied region by 64 bytes depending on direction. Sigalt helpers wrap `sigaltstack`, with checked setup enforcing `STRESS_MINSIGSTKSZ`. Stack size helpers cache computed values, combining Linux `AT_MINSIGSTKSZ`, `sysconf`, compile-time `SIGSTKSZ`, and an absolute 64 KiB floor to account for architectures with large signal frames. The stack-smash override aborts with a message when reporting is enabled, otherwise exits silently. Backtrace uses `backtrace`/`backtrace_symbols` when available and flushes each line.

State and persistence: static cached signal stack sizes and `stress_stack_check_flag` persist. Alternative signal stack state is kernel thread state until disabled or replaced.

Dependencies/integration: uses auxv, execinfo, signal stack APIs, stress logging/fail helpers, and macros such as `STRESS_SIGSTKSZ`.

Risks: stack direction detection is compiler-sensitive, hence noinline/optimize0 safeguards. Weak `__stack_chk_fail` override changes process behavior on stack protector trips. Backtrace is best-effort and not safe for all signal contexts despite small buffers/flushes.

Test signals: stack direction on target architectures, sigaltstack setup below/above minimum, auxv/sysconf fallback values, stack-smash behavior in child process, and builds without execinfo/sigaltstack.
