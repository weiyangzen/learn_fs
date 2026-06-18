# sources/test-tools/strace/tests/clone3-success-Xraw.c

Purpose: `clone3-success-Xraw.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include none detected; macros include `RETVAL_INJECTED`, `XLAT_RAW`; included headers include `clone3.c`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `RETVAL_INJECTED`, `XLAT_RAW`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.  This is a wrapper/variant file that reuses shared test implementation through local includes: `clone3.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `clone3.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. Its filename selects an xlat rendering mode, so the same syscall surface is compared under abbreviated, raw, or verbose symbolic output.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 3 lines, 65 bytes, sha256 prefix `dd7613d55155`.
