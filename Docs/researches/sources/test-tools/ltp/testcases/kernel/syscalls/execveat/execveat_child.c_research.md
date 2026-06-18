# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat_child.c

Purpose: Success sentinel for `execveat01.c` and `execveat03.c`.

Important APIs/types/functions: `TST_NO_DEFAULT_MAIN`, `tst_reinit()`, and `tst_res(TPASS)`.

Control flow: `main()` reinitializes the LTP harness, emits a pass message, and exits 0.

State and persistence behavior: No state is modified; its execution is the observable success of the parent execveat call.

Dependencies and integration points: Used as a resource file copied into test directories and overlay mounts.

Risks and test signals: If a parent expected failure uses this helper accidentally, it would report pass, so negative tests use `execveat_errno.c` instead.
