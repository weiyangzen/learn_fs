# sources/test-tools/ltp/testcases/kernel/syscalls/execvp/execvp01.c

Purpose: Tests successful `execvp()` PATH search with vector-style argv.

Important APIs/types/functions: `SAFE_FORK`, `execvp("execvp01_child", args)`, `tst_brk()`, and `.child_needs_reinit = 1`.

Control flow: The child calls `execvp` by basename with a canary argument. If the call returns, it reports failure.

State and persistence behavior: Runtime state is the PATH lookup environment and argv vector; no persistent files are changed.

Dependencies and integration points: Integrated with `execvp01_child.c` and the LTP test binary staging path.

Risks and test signals: Failure indicates PATH search or exec replacement regressions; the helper detects bad argv.
