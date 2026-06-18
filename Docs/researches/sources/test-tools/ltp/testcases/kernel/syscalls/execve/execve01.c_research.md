# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve01.c

Purpose: Tests that `execve()` passes argv and an explicit environment to the executed binary.

Important APIs/types/functions: `execve(path, args, envp)`, `tst_get_path`, `SAFE_FORK`, `IPC_ENV_VAR`, and LTP error reporting.

Control flow: The parent builds `args = {"execve01_child", "canary", NULL}` and an env containing `LTP_TEST_ENV_VAR=test` plus LTP IPC state, forks, and the child invokes `execve`.

State and persistence behavior: The replacement environment is intentionally minimal; absence of `PATH` is part of the child-side validation.

Dependencies and integration points: Integrated with `execve01_child.c`, which validates argument and environment contracts.

Risks and test signals: Failures expose execve replacement failure, missing helper discovery, or environment leakage/omission.
