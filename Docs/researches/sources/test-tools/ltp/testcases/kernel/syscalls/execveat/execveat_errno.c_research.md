# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_errno.c

Purpose: Failure sentinel for `execveat02.c` negative errno cases.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, and `tst_res(TFAIL)`.

Control flow: `main()` reports that `execveat()` passed unexpectedly and returns 0.

State and persistence behavior: No persistent state; it only proves an expected-failure execveat case reached a new image.

Dependencies and integration points: Used by `execveat02.c` as a resource helper that should never successfully execute.

Risks and test signals: Any run of this helper means the parent accepted an invalid execveat combination.
