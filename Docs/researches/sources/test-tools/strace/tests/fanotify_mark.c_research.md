# sources/test-tools/strace/tests/fanotify_mark.c

Purpose: `fanotify_mark.c` covers fanotify_init and fanotify_mark decoding, including init flags, event masks, mark flags, fd/path variants, and xlat verbosity.

Important APIs/types/functions: local functions include `do_call`, `main`; macros include `str_fan_mark_add`, `str_fan_modify_ondir`, `str_at_fdcwd`, `STR16`, `STR64`; included headers include `tests.h`, `scno.h`, `limits.h`, `stdint.h`, `stdio.h`, `unistd.h`, `sys/fanotify.h`, `secontext.h`. Kernel/user ABI names observed in the full file include `fanotify_mark`. Prominent constants include `SPDX`, `GPL`, `HAVE_SYS_FANOTIFY_H`, `HAVE_FANOTIFY_MARK`, `XLAT_RAW`, `XLAT_VERBOSE`, `FAN_MARK_ADD`, `FAN_MODIFY`, `FAN_ONDIR`, ... (62 total), `SECONTEXT_PID_MY`, `SECONTEXT_FILE`, `SKIP_MAIN_UNDEFINED`; prominent struct names include `strval`, `strval64`.

Control flow: `main` builds deterministic arguments, invokes the target syscall or helper sequence, prints the expected strace line with `printf`/test helpers, and exits through the strace test harness. Variant wrappers select xlat verbosity while the main implementation iterates mark/init flags and fd/path combinations.

State and persistence behavior: runtime state is intentionally temporary and test-local. Most state lives in stack variables, tail-allocated buffers, compile-time macros, and errno/return-code snapshots.

Dependencies: strace test harness headers such as `tests.h`, `scno.h`, `print_utils.h`, `pidns.h`, `secontext.h`, local xlat tables, libc headers, and Linux UAPI headers provide syscall numbers, fallback structs, constants, and output helpers. This file directly includes `tests.h`, `scno.h`, `limits.h`, `stdint.h`, `stdio.h`, `unistd.h`, `sys/fanotify.h`, `secontext.h`.

Integration points: the file participates in strace's testsuite as a compiled C test, AWK normalizer, header, or generator input. It integrates with generated xlat tables, syscall-number selection, test-driver `.test` scripts, and expected-output comparison.

Risks: fanotify availability and permission restrictions vary by kernel and credentials, making graceful skip/error handling as important as the printed mask text.

Test signals: useful validation is the corresponding strace testsuite target under the same basename, comparison of stdout against expected decoder lines, successful compilation under the configured personality/time ABI, and skip behavior when the kernel lacks the syscall or permission. The source was read in full for this report: 283 lines, 6813 bytes, sha256 prefix `6358a0905d14`.
