<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi-success.c -->
# sources/test-tools/strace/tests/ioctl_ubi-success.c

Purpose: Compile-time wrapper for `ioctl_ubi.c`. It does not implement an independent test body; instead it selects abbreviated/default xlat output, fault-injected success output for UBI ioctl decoder coverage for attach, eraseblock, volume, rename, resize, and property requests.

Important APIs/types/functions: The wrapper contributes `INJECT_RETVAL`=42 and then includes `ioctl_ubi.c`. All runtime APIs, helper functions, structures, and syscall/ioctl invocations come from the included translation unit.

Control flow: At preprocessing time the macro definitions alter conditional branches in `ioctl_ubi.c`. Runtime then follows the included file's `main` and helper functions exactly, with output formatting changed by the wrapper-selected mode.

State/persistence behavior: This file has no standalone runtime state. Any state, temporary kernel objects, file descriptors, allocated buffers, or cleanup behavior are inherited from `ioctl_ubi.c`.

Dependencies: Depends on `ioctl_ubi.c` remaining includable as a single translation unit and honoring the selected macros. It also depends on the strace test harness building this wrapper as a distinct executable or expected-output variant.

Integration points: Provides separate test coverage for the same decoder surface under a different strace output mode, success-injection mode, verbose-field mode, or namespace-translation mode. This is important because strace's raw, abbreviated, and verbose xlat paths are separate formatting paths.

Risks: Wrapper drift is easy to miss: a renamed base file, changed macro contract, or missing wrapper variant can silently reduce mode coverage. Because this source is only 2 line(s) and 48 bytes, substantive behavior must be understood through `ioctl_ubi.c`.

Test signals: The expected signal is successful compilation plus output equivalent to `ioctl_ubi.c` under abbreviated/default xlat output, fault-injected success output. Regressions appear as xlat spelling differences, missing `(INJECTED)` markers, missing verbose fields, or lost PID namespace annotations.

Source read signal: complete file read for this research pass; file size 2 line(s), 48 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_ubi-success.c -->
