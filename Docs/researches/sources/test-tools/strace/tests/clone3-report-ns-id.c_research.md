# sources/test-tools/strace/tests/clone3-report-ns-id.c

Purpose: `clone3-report-ns-id.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include `main`; macros include none detected; included headers include `tests.h`, `xmalloc.h`, `limits.h`, `stdio.h`, `unistd.h`, `linux/sched.h`, `scno.h`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `SPDX`, `GPL`, `CLONE_NEWUSER`, `PATH_MAX`, `NULL`; prominent struct names include `clone_args`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `xmalloc.h`, `limits.h`, `stdio.h`, `unistd.h`, `linux/sched.h`, `scno.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 44 lines, 1107 bytes, sha256 prefix `8a8877d5598e`.
