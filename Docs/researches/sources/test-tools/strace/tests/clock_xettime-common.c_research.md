# sources/test-tools/strace/tests/clock_xettime-common.c

Purpose: `clock_xettime-common.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include `k_syscall`, `k_getres`, `k_gettime`, `k_settime`, `main`; macros include none detected; included headers include `stdio.h`, `time.h`, `unistd.h`, `kernel_timespec.h`. Kernel/user ABI names observed in the full file include `clock_gettime`. Prominent constants include `SPDX`, `GPL`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `CLOCK_MONOTONIC`, `NULL`, `CLOCK_REALTIME`, `CLOCK_PROCESS_CPUTIME_ID`, `CLOCK_THREAD_CPUTIME_ID`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `stdio.h`, `time.h`, `unistd.h`, `kernel_timespec.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 116 lines, 3505 bytes, sha256 prefix `8792e3495a04`.
