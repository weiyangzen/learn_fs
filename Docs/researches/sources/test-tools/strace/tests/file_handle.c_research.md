# sources/test-tools/strace/tests/file_handle.c

Purpose: `file_handle.c` checks name_to_handle_at/open_by_handle_at decoding, handle buffer sizes, mount ids, flags, and optional SELinux context annotations.

Important APIs/types/functions: local functions include `print_handle_data`, `do_name_to_handle_at`, `do_open_by_handle_at`, `main`; macros include `MAX_HANDLE_SZ`, `STR16`, `STR64`; included headers include `tests.h`, `scno.h`, `assert.h`, `errno.h`, `inttypes.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `chdir`, `fchdir`, `fcntl`, `name_to_handle_at`, `open_by_handle_at`. Prominent constants include `SPDX`, `GPL`, `ASSERT_NONE`, `ASSERT_SUCCESS`, `ASSERT_ERROR`, `MAX_HANDLE_SZ`, `MIN`, `TEST_SECONTEXT`, `NULL`, ... (31 total), `F8ILL_KULONG_MASK`, `O_WRONLY`, `ARRAY_SIZE`; prominent struct names include `file_handle`, `strval`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The main path first probes `name_to_handle_at` error behavior, then allocates several handle buffers to cover overflow, valid data, invalid pointers, and `open_by_handle_at` formatting.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal. Opaque file handles and mount ids are kernel/filesystem outputs and are printed, not persisted.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `assert.h`, `errno.h`, `inttypes.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: file handles are filesystem-dependent and may require capabilities for open_by_handle_at; tests must preserve EOVERFLOW, EINVAL, and success distinctions without assuming stable opaque handle bytes.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 408 lines, 11725 bytes, sha256 prefix `ba4eed4fcb9e`.
