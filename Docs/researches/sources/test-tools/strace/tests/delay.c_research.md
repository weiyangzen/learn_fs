# sources/test-tools/strace/tests/delay.c

Purpose: `delay.c` drives process-control or harness behavior needed by strace tests, such as vfork detach, delay/timing, or sanitized environment execution.

Important APIs/types/functions: local functions include `check_expected`, `check_expectations`, `check_delay`, `do_child`, `run_checks`, `main`, `usecs_from_tv`, `usecs_from_ts`; macros include none detected; included headers include `tests.h`, `errno.h`, `inttypes.h`, `limits.h`, `stdio.h`, `stdint.h`, `stdlib.h`, ... (13 total), `sys/wait.h`, `scno.h`, `kernel_timeval.h`. Kernel/user ABI names observed in the full file include `clock_gettime`. Prominent constants include `SPDX`, `GPL`, `BAD_OTHER`, `DELAY_ENTER_TOO_SHORT`, `DELAY_EXIT_TOO_SHORT`, `DELAY_ENTER_TOO_LONG`, `DELAY_EXIT_TOO_LONG`, `MASK_DELAY_TOO_LONG`, `NULL`, ... (14 total), `WIFEXITED`, `WEXITSTATUS`, `ECHILD`; prominent struct names include `timespec`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `inttypes.h`, `limits.h`, `stdio.h`, `stdint.h`, `stdlib.h`, ... (13 total), `sys/wait.h`, `scno.h`, `kernel_timeval.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 188 lines, 4203 bytes, sha256 prefix `08fdbb9bbc0d`.
