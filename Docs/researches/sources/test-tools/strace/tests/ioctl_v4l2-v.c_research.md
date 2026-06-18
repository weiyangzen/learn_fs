<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v.c -->
# sources/test-tools/strace/tests/ioctl_v4l2-v.c

Purpose: Compile-time wrapper for `ioctl_v4l2.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, verbose structure-field output for negative-path V4L2 ioctl decoder coverage with failed ioctls and xlat-mode-sensitive output.

Important APIs/types/functions: The wrapper contributes `VERBOSE`=1 and then includes `ioctl_v4l2.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_v4l2.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_v4l2.c`.

Dependencies: Depends on `ioctl_v4l2.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 3 line(s) and 95 bytes, substantive behavior must be understood through `ioctl_v4l2.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_v4l2.c` under abbreviated/default xlat output, verbose structure-field output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 3 line(s), 95 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_v4l2-v.c -->
