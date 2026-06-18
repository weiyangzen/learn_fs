# sources/test-tools/ltp/testcases/kernel/syscalls/execveat/execveat.h

Purpose: Provides a feature probe for `execveat()` support.

Important APIs/types/functions: `execveat(-1, "", NULL, NULL, AT_EMPTY_PATH)`, `errno`, and `tst_brk(TCONF)`.

Control flow: `check_execveat()` calls an intentionally invalid execveat form and treats `EINVAL` as meaning the syscall is not supported by the current environment.

State and persistence behavior: No persistent state; it is a runtime capability gate shared by execveat tests.

Dependencies and integration points: Included by all execveat parent test sources before they set up filesystem scenarios.

Risks and test signals: The probe distinguishes unsupported syscall behavior from later testcase errors. If errno conventions change, capability detection could misclassify support.
