# sources/test-tools/strace/tests/clock_adjtime64.c

Purpose: `clock_adjtime64.c` exercises clock and time syscall decoders, especially clock ids, timespec/timex structures, 32-bit versus 64-bit time ABI variants, and restartable sleep output.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`; included headers include `tests.h`, `scno.h`, `clock_adjtime-common.c`. Kernel/user ABI names observed in the full file include `clock_adjtime`. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `clock_adjtime-common.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `clock_adjtime-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: time64/time32 splits and architecture-specific clock ids can alter syscall numbers and structure layout, so tests need conditional compilation and tolerant unsupported-syscall handling.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 24 lines, 418 bytes, sha256 prefix `5bd5f0eb5767`.
