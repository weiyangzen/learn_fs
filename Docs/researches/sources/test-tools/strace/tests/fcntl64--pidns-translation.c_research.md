# sources/test-tools/strace/tests/fcntl64--pidns-translation.c

Purpose: `fcntl64--pidns-translation.c` is shared or variant coverage for fcntl/fcntl64 command decoding, flock structures, owner records, seals, leases, pipe size, pid namespace translation, and unknown commands.

Important APIs/types/functions: local functions include none detected; macros include `PIDNS_TRANSLATION`; included headers include `fcntl64.c`. Kernel/user ABI names observed in the full file include `fcntl64`. Prominent constants include `PIDNS_TRANSLATION`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The common fcntl body dispatches command-specific helpers for flock, flock64/OFD, ownership, seals, leases, pipe sizing, and unknown commands; pid namespace helpers prepend translated pid context when enabled.  This is a wrapper/variant file that reuses shared test implementation through local includes: `fcntl64.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `fcntl64.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fcntl structures differ across ABIs and pid namespace translation changes expected pid text, so offset widths, flock64 availability, and owner pid rendering are the main regression risks.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 2 lines, 47 bytes, sha256 prefix `f2b03a0668db`.
