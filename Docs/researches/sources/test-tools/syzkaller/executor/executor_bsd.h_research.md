# sources/test-tools/syzkaller/executor/executor_bsd.h

Purpose: FreeBSD, NetBSD, and OpenBSD executor adapter for data mapping, syscall dispatch, and KCOV-style coverage.

Important APIs and control flow: `os_init` maps the executor data region with platform-specific W^X handling, raises `RLIMIT_NOFILE`, and installs a SIGCHLD handler. `execute_syscall` calls pseudo-syscalls directly or platform syscall entry points. `cover_open`, `cover_mmap`, `cover_protect`, `cover_unprotect`, `cover_enable`, `cover_reset`, and `cover_collect` adapt FreeBSD `/dev/kcov`, OpenBSD kcov ioctls, and NetBSD remote VHCI coverage. NetBSD declares `features` for USB emulation and fault injection plus no-op setup hooks.

State and dependencies: `cover_t` stores fd, mmap address, data size, offsets, and overflow state shared with `executor.cc`. The implementation depends on BSD kcov headers/ioctls, `MAP_FIXED_EXCLUSIVE`, and platform feature macros.

Integration points: included by `executor.cc` for `GOOS_freebsd`, `GOOS_netbsd`, and `GOOS_openbsd`; NetBSD USB integrates with `common_usb_netbsd.h`.

Risks and tests: OpenBSD does not support raw syscall fallback for missing call wrappers and fails instead. Protection is implemented only for FreeBSD/OpenBSD and not NetBSD. NetBSD extra coverage uses fixed VHCI remote IDs. Test signals are mostly cross-target executor builds plus runtime coverage/machine checks.
