# sources/test-tools/ltp/testcases/kernel/syscalls/execve/execve06.c

Purpose: Regression test for empty-argv `execve()` handling related to CVE-2021-4034: the kernel should synthesize a non-null `argv[0]`.

Important APIs/types/functions: `execve(path, argv, envp)` with `argv[] = {NULL}`, `tst_get_path`, `SAFE_FORK`, `IPC_ENV_VAR`, and LTP tags for the fixing kernel commit/CVE.

Control flow: The child process calls `execve` on `execve06_child` with an empty argument list and a minimal environment. If exec succeeds, the helper validates argc/argv.

State and persistence behavior: Process argument vector normalization is the state under test; there is no filesystem mutation beyond locating the helper.

Dependencies and integration points: Integrated with `execve06_child.c` and LTP metadata tags `linux-git dcd46d897adb` and `CVE 2021-4034`.

Risks and test signals: A vulnerable or regressed kernel may present `argc == 0` or `argv[0] == NULL`, which the child reports as failure.
