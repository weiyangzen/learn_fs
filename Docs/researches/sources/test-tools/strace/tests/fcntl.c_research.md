# sources/test-tools/strace/tests/fcntl.c

Purpose: `fcntl.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include `test_flock64_undecoded`, `test_flock64_lk64`; macros include `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `TEST_FLOCK64_UNDECODED`; included headers include `tests.h`, `scno.h`, `fcntl-common.c`. Kernel/user ABI names observed in the full file include `fcntl`. Prominent constants include `SPDX`, `GPL`, `TEST_SYSCALL_NR`, `TEST_SYSCALL_STR`, `F_SETLK64`, `F_GETOWN_EX`, `F_SETLKW64`, `F_GETLK`, `F_GETLK64`, ... (15 total), `ETOWN_EX`, `ETLK64`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `flock64`.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `fcntl-common.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 62 lines, 1683 bytes, sha256 prefix `1fe22cb569fe`.
