# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/os/CMakeLists.txt

Purpose: this CMake file selects and builds platform-specific VFS handle syscall support.

Important behavior: when `FREEBSD` is set, `freebsd/handle_syscalls.c` is used; when `LINUX` is set, `linux/handle_syscalls.c` is used. The selected source is built as an object library `fsal_os` with sanitizers and `-fPIC`. LTTng-generated headers are added as dependencies when tracing is enabled.

Control flow and state: build-time platform selection determines the runtime persistent-handle format and syscalls. No runtime state is stored here.

Dependencies and integration points: the `fsal_os` object library is linked into VFS and Lustre FSAL modules by `vfs/CMakeLists.txt`.

Risks: exactly one platform source must be selected; missing `LINUX`/`FREEBSD` leaves `fsal_os_STAT_SRCS` empty. Handle format incompatibilities are platform-defined, so mixed build/runtime assumptions are unsafe.

Test signals: configure Linux and FreeBSD builds, verify `fsal_os` has one source, and run handle create/open/recreate tests on each platform.
