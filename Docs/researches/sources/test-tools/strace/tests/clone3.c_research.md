# sources/test-tools/strace/tests/clone3.c

Purpose: `clone3.c` drives clone3 decoder coverage across raw, abbreviated, verbose, injected-success, namespace-id-reporting, and invalid-argument cases.

Important APIs/types/functions: local functions include `wait_cloned`, `do_clone3_`, `print_addr64`, `print_tls`, `print_set_tid`, `print_clone3`, `main`; macros include `VERBOSE`, `RETVAL_INJECTED`, `MAX_SET_TID_SIZE`, `INJ_STR`, `ERR`, `do_clone3`; included headers include `tests.h`, `errno.h`, `stdint.h`, `inttypes.h`, `stdio.h`, `string.h`, `unistd.h`, ... (11 total), `linux/sched.h`, `asm/ldt.h`, `scno.h`. Kernel/user ABI names observed in the full file include `clone3`. Prominent constants include `SPDX`, `GPL`, `HAVE_STRUCT_USER_DESC`, `VERBOSE`, `RETVAL_INJECTED`, `STRUCT_VALID_BIT`, `PIDFD_VALID_BIT`, `CHILD_TID_VALID_BIT`, `PARENT_TID_VALID_BIT`, ... (66 total), `ARRAY_SIZE`, `XLAT_FMT_U`, `XLAT_ARGS`; prominent struct names include `clone_args`, `user_desc`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. `do_clone3_` centralizes syscall execution, expected errno masks, injected-return handling, child exit, and parent wait logic; `print_clone3` mirrors decoder output for every tested argument shape.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. clone/clone3 tests create real child tasks for success cases and must wait/reap them to avoid stray processes.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `errno.h`, `stdint.h`, `inttypes.h`, `stdio.h`, `string.h`, `unistd.h`, ... (11 total), `linux/sched.h`, `asm/ldt.h`, `scno.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: clone3 behavior is kernel, architecture, and seccomp dependent; success paths fork real children and require careful wait handling, while xlat verbosity macros must match the generated test variant.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 601 lines, 17156 bytes, sha256 prefix `9572a76ecf18`.
