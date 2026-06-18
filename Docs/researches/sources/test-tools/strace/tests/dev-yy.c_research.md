# sources/test-tools/strace/tests/dev-yy.c

Purpose: `dev-yy.c` checks `--decode-fds` output modes for device, path, socket, pty, and disabled decoding forms.

Important APIs/types/functions: local functions include `main`; macros include `PRINT_PATH`, `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`, `DEV_FMT`; included headers include `tests.h`, `stdio.h`, `unistd.h`, `scno.h`, `linux/fcntl.h`, `sys/sysmacros.h`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `SPDX`, `GPL`, `PRINT_PATH`, `PRINT_DEVNUM`, `PRINT_AT_FDCWD_PATH`, `DEV_FMT`, `O_PATH`, `ARRAY_SIZE`, `AT_FDCWD`, `O_RDONLY`, `SKIP_MAIN_UNDEFINED`; prominent struct names include none detected.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `stdio.h`, `unistd.h`, `scno.h`, `linux/fcntl.h`, `sys/sysmacros.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 129 lines, 2410 bytes, sha256 prefix `41a922f7f2a5`.
