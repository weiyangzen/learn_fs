# sources/test-tools/strace/tests/epoll_pwait2-y.c

Purpose: `epoll_pwait2-y.c` covers epoll creation, control, wait, pwait, and pwait2 decoders, including event masks, timeout structures, sigmask pointers, and fd/path variants.

Important APIs/types/functions: local functions include none detected; macros include `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; included headers include `epoll_pwait2.c`. Kernel/user ABI names observed in the full file include `epoll_pwait2`. Prominent constants include `FD9_PATH`, `SKIP_IF_PROC_IS_UNAVAILABLE`; prominent struct names include none detected.

Control flow: this file is a shared implementation or variant wrapper; compile-time macros select the syscall number, xlat style, fd/path mode, success behavior, or namespace mode before the included/shared test body runs. The epoll tests create descriptors/events, drive control or wait calls, and print event masks, timeout values, and signal-mask arguments in the same shape strace should decode.  This is a wrapper/variant file that reuses shared test implementation through local includes: `epoll_pwait2.c`.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `epoll_pwait2.c`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison. The variant also exercises path/fd decoding options such as `-P`, `-y`, `-yy`, or `--decode-fds`.

Risks: Primary risks are kernel/architecture feature availability, ABI-width differences, host header drift, permissions, namespace-dependent pid/fd/path rendering, and expected-output brittleness when symbolic constants change.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 4 lines, 132 bytes, sha256 prefix `1fb9b6dc3e24`.
