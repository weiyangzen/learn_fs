# sources/test-tools/xfstests-bld/fstests-bld/android-compat/quota.h

Purpose: minimal quota API header for Android builds lacking Linux quota definitions.

Important APIs and functions: defines quota type constants, `QCMD`, quota command constants, `QIF_*` and `IIF_*` masks, `struct dqblk`, shorthand field macros, `dqoff`, `struct dqinfo`, and `quotactl` prototype.

Control flow: preprocessor definitions and type declarations only.

State and persistence: no runtime state. Defines ABI layout expectations for quota tools.

Dependencies and integration: included by `quotactl.c` and installed as `sys/quota.h` by the android-compat Makefile.

Risks: structure layouts and command values must match kernel expectations. The header is intentionally minimal and may omit fields or commands needed by newer quota utilities.

Test signals: quota tools compile and link; runtime quota syscalls receive correctly shaped data structures.
