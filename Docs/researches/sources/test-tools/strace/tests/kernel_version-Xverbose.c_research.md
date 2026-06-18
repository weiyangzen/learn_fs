<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xverbose.c -->
# sources/test-tools/strace/tests/kernel_version-Xverbose.c

Purpose: Compile-time wrapper for `kernel_version.c`. It does not implement an independent test body; instead it selects verbose xlat output for BPF/kernel-version formatting coverage.

Important APIs/types/functions: The wrapper contributes `XLAT_VERBOSE`=1 and then includes `kernel_version.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `kernel_version.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `kernel_version.c`.

Dependencies: Depends on `kernel_version.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 51 bytes, substantive behavior must be understood through `kernel_version.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `kernel_version.c` under verbose xlat output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 51 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/kernel_version-Xverbose.c -->
