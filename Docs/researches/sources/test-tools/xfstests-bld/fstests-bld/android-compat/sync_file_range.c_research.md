# sources/test-tools/xfstests-bld/fstests-bld/android-compat/sync_file_range.c

Purpose: exposes `sync_file_range` on Android by forwarding to the kernel syscall.

Important APIs and functions: exports `int sync_file_range(int fd, off64_t offset, off64_t nbytes, unsigned int flags)`.

Control flow: returns `syscall(SYS_sync_file_range, fd, offset, nbytes, flags)`.

State and persistence: requests writeback/synchronization of file ranges through the kernel; no local state.

Dependencies and integration: depends on syscall headers and `android_compat.h`; used by filesystem tools that call `sync_file_range`.

Risks: syscall availability and argument ABI can vary by architecture/kernel. Errors are returned directly through syscall conventions.

Test signals: compile/link success and runtime calls returning expected kernel success or errno.
