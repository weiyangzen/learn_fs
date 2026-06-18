<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xraw.c -->
# sources/test-tools/strace/tests/ipc_sem-Xraw.c

Purpose: Compile-time wrapper for `ipc_sem.c`. It does not implement an independent test body; instead it selects raw xlat output for SysV semaphore decoder coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_RAW`=1 and then includes `ipc_sem.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ipc_sem.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ipc_sem.c`.

Dependencies: Depends on `ipc_sem.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 40 bytes, substantive behavior must be understood through `ipc_sem.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ipc_sem.c` under raw xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 40 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_sem-Xraw.c -->
