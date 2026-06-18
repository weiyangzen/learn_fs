<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/accept4.c -->
## sources/test-tools/strace/tests/accept4.c

Purpose: Tests `accept4` decoding by reusing the common accept test body with an extra flags argument.

Important APIs/types/functions: Includes `kernel_fcntl.h`, guards on `HAVE_ACCEPT4`, defines `TEST_SYSCALL_NAME accept4`, `SUFFIX_ARGS , O_CLOEXEC`, and `SUFFIX_STR ", SOCK_CLOEXEC"`, then includes `accept.c`.

Control flow: If `accept4` is available, compilation specializes `accept.c` so calls include `O_CLOEXEC` and expected output includes `SOCK_CLOEXEC`. Otherwise it emits a skip main.

State and persistence: Same Unix socket lifecycle as `accept.c`; no additional state.

Dependencies and integration: Wrapper integrated by `Makefile.am` as its own executable; depends on accept test macro hooks.

Risks: Macro coupling is tight: changes in `accept.c` suffix hooks can break this variant. Availability is configure/kernel dependent.

Test signals: Traced output should show `accept4(..., SOCK_CLOEXEC)` decoding and normal socket cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/accept4.c -->
