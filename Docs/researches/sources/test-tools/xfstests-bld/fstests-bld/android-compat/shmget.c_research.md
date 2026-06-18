# sources/test-tools/xfstests-bld/fstests-bld/android-compat/shmget.c

Purpose: supplies System V shared memory wrappers for Android/bionic builds.

Important APIs and functions: exports `shmctl`, `shmat`, `shmdt`, and `shmget`, each forwarding to the matching `SYS_*` syscall.

Control flow: each wrapper calls `syscall` with the provided arguments. `shmat` currently calls `syscall(SYS_shmat, ...)` but does not return the result.

State and persistence: operations create, attach, detach, or control kernel shared memory segments. The file maintains no local state.

Dependencies and integration: depends on `sys/glibc-syscalls.h`, syscall numbers, and `android_compat.h`; used by programs requiring SysV IPC.

Risks: missing return in `shmat` is a correctness bug and can corrupt callers' attached address handling. SysV IPC availability varies on Android kernels.

Test signals: compile/link success plus runtime shared-memory tests; `shmat` should be specifically validated.
