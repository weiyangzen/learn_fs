# sources/test-tools/ltp/testcases/kernel/syscalls/execl/execl01.c

Purpose: Tests successful `execl()` replacement of a forked child with a helper binary and varargs argument passing.

Important APIs/types/functions: `tst_get_path()`, `SAFE_FORK`, `execl(path, "execl01_child", "canary", NULL)`, `TEST()`, and LTP fork reinitialization settings.

Control flow: The parent locates `execl01_child`, forks, and the child calls `execl`. If `execl` returns, the child reports `TFAIL`; otherwise the helper validates the canary.

State and persistence behavior: Process image replacement and argv contents are the only state under test. The test sets unlimited stack via `.ulimit` to avoid environment-specific exec argument stack issues.

Dependencies and integration points: Integrated with `execl01_child.c` and `$PATH` resource discovery.

Risks and test signals: Failure can be an inability to locate the helper, failed exec, or child-side argument mismatch. Successful exec is signaled by the helper's `TPASS`.
