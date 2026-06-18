# sources/test-tools/strace/tests/fadvise64.c

Purpose: `fadvise64.c` covers fadvise64/fadvise64_64 argument layout and advice-name decoding across ABI layouts.

Important APIs/types/functions: local functions include `do_fadvise`; macros include none detected; included headers include `tests.h`, `scno.h`, `fadvise.h`. Kernel/user ABI names observed in the full file include `fadvise64`. Prominent constants include `SPDX`, `GPL`, `LONG_MAX`, `INT_MAX`, `LINUX_MIPSN32`, `LINUX_MIPSO32`, `LL_VAL_TO_PAIR`, `X32`, `POWERPC`, `POSIX_FADV_`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fadvise.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 57 lines, 1533 bytes, sha256 prefix `9e4b75a9e827`.
