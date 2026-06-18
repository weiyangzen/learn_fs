# sources/test-tools/ltp/testcases/kernel/syscalls/execlp/execlp01.c

Purpose: Tests successful `execlp()` PATH search and varargs argument passing.

Important APIs/types/functions: `SAFE_FORK`, `execlp("execlp01_child", ...)`, `TEST()`, `tst_brk()`, and `.child_needs_reinit = 1`.

Control flow: The parent forks; the child calls `execlp` by basename, relying on the test environment PATH. Returning from exec is a failure.

State and persistence behavior: No durable state is used. The process search path and argv are the relevant runtime state.

Dependencies and integration points: Integrated with `execlp01_child.c` and LTP's resource installation/path setup.

Risks and test signals: Failures point to PATH lookup, exec failure, or child-side canary mismatch.
