# sources/test-tools/strace/tests/fcntl-common.c

Purpose: `fcntl-common.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include `invoke_test_syscall`, `test_flock_einval`, `test_flock64_einval`, `test_flock`, `test_flock64_ofd`, `test_flock64_lk64`, `test_flock64`, `test_f_owner_ex_type_pid`, `test_f_owner_ex_umove_or_printaddr`, ... (26 total), `test_fcntl_others`, `create_sample`, `main`; macros include `FILE_LEN`, `TEST_FLOCK_EINVAL`, `TEST_FLOCK64_EINVAL`, `NEED_TEST_FLOCK64_EINVAL`, `TYPEOF_FLOCK_OFF_T`; included headers include `stdio.h`, `stdint.h`, `inttypes.h`, `stdlib.h`, `string.h`, `unistd.h`, `assert.h`, `linux/fcntl.h`, `pidns.h`, `scno.h`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `SPDX`, `GPL`, `FILE_LEN`, `TEST_FLOCK_EINVAL`, `TEST_FLOCK64_EINVAL`, `NEED_TEST_FLOCK64_EINVAL`, `F_OFD_GETLK`, `F_OFD_SETLK`, `F_OFD_SETLKW`, ... (74 total), `F_GETLEASE`, `F_GETSIG`, `PIDNS_TEST_INIT`; prominent struct names include `flock`, `flock64`, `f_owner_ex`, `fcntl_cmd_check`, `strval64`, `delegation`, `strval32`, `strval16`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.

State and persistence behavior: runtime state is intentionally temporary and test-local. The test may allocate tail buffers and/or create temporary files, directories, descriptors, sockets, eventfds, epoll instances, or mount/file handles, then relies on process exit or explicit cleanup for disposal.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `stdio.h`, `stdint.h`, `inttypes.h`, `stdlib.h`, `string.h`, `unistd.h`, `assert.h`, `linux/fcntl.h`, `pidns.h`, `scno.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 609 lines, 16852 bytes, sha256 prefix `6cb185791b3e`.
