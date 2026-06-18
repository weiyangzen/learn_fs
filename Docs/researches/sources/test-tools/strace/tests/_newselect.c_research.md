<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect.c -->
## sources/test-tools/strace/tests/_newselect.c

Purpose: Select-family decoder entry point for the Linux `_newselect` syscall.

Important APIs/types/functions: Includes `tests.h`, `scno.h`, guards on `__NR__newselect`, defines `TEST_SYSCALL_NR` and `TEST_SYSCALL_STR`, and includes shared `xselect.c`.

Control flow: If `_newselect` exists, the generic select test body is compiled for that syscall number/name. Otherwise `SKIP_MAIN_UNDEFINED("__NR__newselect")` provides a skip main.

State and persistence: No persistent state; runtime state is provided by `xselect.c` allocations and fd sets.

Dependencies and integration: Integrates the architecture syscall table, shared select decoder tests, and wrapper variants like `_newselect-P.c`.

Risks: Coverage depends on `xselect.c` accurately handling syscall-specific ABI differences. Architectures without `__NR__newselect` intentionally skip.

Test signals: Build should compile either a runnable `_newselect` test or a skip binary; traced output should show `_newselect` argument decoding.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/_newselect.c -->
