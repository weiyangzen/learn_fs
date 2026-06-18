# sources/test-tools/strace/tests/faccessat2.c

Purpose: `faccessat2.c` validates faccessat/faccessat2 decoder output for dirfd, path, mode, flags, and path-decoding variants.

Important APIs/types/functions: local functions include `k_faccessat2`, `main`; macros include `XLAT_MACROS_ONLY`, `FD_PATH`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `tests.h`, `scno.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `xlat/faccessat_flags.h`. Kernel/user ABI names observed in the full file include `faccessat2`, `fcntl`. Prominent constants include `SPDX`, `GPL`, `XLAT_MACROS_ONLY`, `FD_PATH`, `YFLAG`, `SKIP_IF_PROC_IS_UNAVAILABLE`, `TAIL_ALLOC_OBJECT_CONST_PTR`, `O_WRONLY`, `AT_FDCWD`, ... (21 total), `NULL`, `ARRAY_SIZE`, `PATH_TRACING`; prominent struct names include `strival32`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The path/fd variants allocate stable pathnames or descriptors, run failing and successful forms where possible, and print both symbolic flags and raw fallback bits.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `xmalloc.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `xlat/faccessat_flags.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 165 lines, 3990 bytes, sha256 prefix `4c6148eb426a`.
