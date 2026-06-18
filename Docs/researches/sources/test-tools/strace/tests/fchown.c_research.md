# sources/test-tools/strace/tests/fchown.c

Purpose: `fchown.c` validates ownership-changing syscall decoders and 32-bit compatibility variants, including uid/gid sentinel and path/fd forms.

Important APIs/types/functions: local functions include none detected; macros include `SYSCALL_NR`, `SYSCALL_NAME`, `ACCESS_BY_DESCRIPTOR`, `UGID_TYPE_IS_SHORT`; included headers include `tests.h`, `scno.h`, `xchownx.c`. Kernel/user ABI names observed in the full file include `fchown`. Prominent constants include `SPDX`, `GPL`, `SYSCALL_NR`, `SYSCALL_NAME`, `ACCESS_BY_DESCRIPTOR`, `UGID_TYPE_IS_SHORT`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.  This is a wrapper/variant file that reuses shared test implementation through local includes: `tests.h`, `scno.h`, `xchownx.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xchownx.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 27 lines, 452 bytes, sha256 prefix `c9bc95453783`.
