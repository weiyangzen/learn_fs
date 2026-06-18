# sources/test-tools/strace/tests/cur_audit_arch.h

Purpose: `cur_audit_arch.h` is a shared test header that supplies architecture-specific constants or helper declarations to generated/compiled strace tests.

Important APIs/types/functions: local functions include none detected; macros include `STRACE_TESTS_CUR_AUDIT_ARCH_H`, `CUR_AUDIT_ARCH`, `CUR_AUDIT_ARCH_STR`, `M32_AUDIT_ARCH`, `M32_AUDIT_ARCH_STR`, `M32__NR_gettid`, `PERS0_AUDIT_ARCH`, ... (12 total), `MX32_AUDIT_ARCH`, `MX32_AUDIT_ARCH_STR`, `MX32__NR_gettid`; included headers include `linux/audit.h`. Kernel/user ABI names observed in the full file include none detected. Prominent constants include `AUDIT_ARCH_`, `CUR_AUDIT_ARCH`, `SPDX`, `GPL`, `STRACE_TESTS_CUR_AUDIT_ARCH_H`, `CUR_AUDIT_ARCH_STR`, `PERS0_AUDIT_ARCH`, `PERS0_AUDIT_ARCH_STR`, `M32_AUDIT_ARCH`, ... (46 total), `AUDIT_ARCH_XTENSA`, `HAVE_M32_MPERS`, `HAVE_MX32_MPERS`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `linux/audit.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 212 lines, 7021 bytes, sha256 prefix `bf5b27da3a3a`.
