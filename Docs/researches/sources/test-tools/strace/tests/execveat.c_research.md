# sources/test-tools/strace/tests/execveat.c

Purpose: `execveat.c` checks execve and execveat argument/envp/path decoding, verbose argument rendering, and AT_* flag behavior.

Important APIs/types/functions: local functions include `k_execveat`, `tests_with_existing_file`, `main`; macros include `FILENAME`, `Q_FILENAME`; included headers include `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `execveat`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `SECONTEXT_PID_MY`, `O_RDONLY`, `O_CREAT`, `SECONTEXT_FILE`, `NULL`, `AT_FDCWD`, `FILENAME`, ... (18 total), `DEFAULT_STRLEN`, `AT_EXECVE_CHECK`, `AT_`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The exec tests stage argv/envp/pathname combinations and use controlled failure or child execution so the trace line can be compared without losing the harness process unexpectedly.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. exec tests intentionally manipulate process image boundaries and environment vectors, so their persistence boundary is the child/process invocation.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: exec tests replace the process image on success, so they rely on controlled failing paths or child execution and must preserve argv/envp quoting and truncation expectations.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 308 lines, 8149 bytes, sha256 prefix `8b33106cb9ac`.
