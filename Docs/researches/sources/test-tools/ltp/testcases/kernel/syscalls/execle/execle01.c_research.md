# sources/test-tools/ltp/testcases/kernel/syscalls/execle/execle01.c

Purpose: Tests `execle()` argument passing and explicit environment replacement.

Important APIs/types/functions: `execle()`, `tst_get_path`, `SAFE_FORK`, `IPC_ENV_VAR`, and an `envp` containing `LTP_TEST_ENV_VAR=test` plus the LTP IPC variable.

Control flow: The parent builds a minimal environment, locates the helper, forks, and the child invokes `execle`. Returning from exec is reported as a failure.

State and persistence behavior: The environment vector is the important transient state; it deliberately omits `PATH` while preserving the LTP IPC variable needed by `tst_reinit()`.

Dependencies and integration points: Works with `execle01_child.c`, which checks argv and environment content.

Risks and test signals: Risk is omitting harness-required IPC state or accidentally inheriting environment variables. The child catches missing custom env and unexpected `PATH`.
