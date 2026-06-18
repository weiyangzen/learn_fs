<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp-y--pidns-translation.c -->
# sources/test-tools/strace/tests/kcmp-y--pidns-translation.c

Purpose: Compile-time wrapper for `kcmp-y.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, PID namespace translation for verbose-fd kcmp decoder coverage.

Important APIs/types/functions: The wrapper contributes `PIDNS_TRANSLATION`=#include "kcmp-y.c" and then includes `kcmp-y.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `kcmp-y.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `kcmp-y.c`.

Dependencies: Depends on `kcmp-y.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 46 bytes, substantive behavior must be understood through `kcmp-y.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `kcmp-y.c` under abbreviated/default xlat output, PID namespace translation. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 46 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kcmp-y--pidns-translation.c -->
