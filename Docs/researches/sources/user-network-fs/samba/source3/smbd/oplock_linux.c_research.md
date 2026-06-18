# sources/user-network-fs/samba/source3/smbd/oplock_linux.c

## Purpose
`oplock_linux.c` provides Samba `smbd` support for Linux kernel oplocks, implemented with Linux file leases. When compiled with `HAVE_KERNEL_OPLOCKS_LINUX`, it sets lease signal delivery, requests and releases kernel leases through the VFS `linux_setlease` hook, and wires Linux lease-break signals back into Samba’s oplock break path.

When kernel oplocks are not available at build time, the file only provides an empty dummy symbol so the compilation unit remains valid.

## Important APIs, Types, And Functions
`linux_set_lease_sighandler(int fd)` sets `F_SETSIG` to `RT_SIGNAL_LEASE` for a file descriptor. `linux_setlease(int fd, int leasetype)` temporarily becomes root, installs the signal target, calls `fcntl(fd, F_SETLEASE, leasetype)`, preserves `errno`, and then drops root privileges.

`linux_oplock_signal_handler()` is a tevent signal callback for `RT_SIGNAL_LEASE`. It extracts `si_fd`, finds the matching `files_struct` with `file_find_fd()`, and calls `break_kernel_oplock()` through the server connection messaging context.

`linux_set_kernel_oplock()` requests `F_WRLCK` through `SMB_VFS_LINUX_SETLEASE()` and logs the file id/gen id. `linux_release_kernel_oplock()` optionally logs current `F_GETLEASE` state and releases the lease with `F_UNLCK`. `linux_oplocks_available()` probes `/dev/null` with `F_GETLEASE`. `linux_init_kernel_oplocks()` allocates `struct kernel_oplocks`, assigns `linux_koplocks`, stores the `smbd_server_connection`, registers the tevent signal handler, and returns the context.

## Control Flow
Initialization starts when `init_kernel_oplocks()` in `smb2_oplock.c` calls `linux_init_kernel_oplocks()` if configuration and platform checks allow it. The initializer probes support, allocates context, and registers a realtime signal handler with `SA_SIGINFO`.

On granting an oplock, higher-level oplock code calls the `kernel_oplocks_ops.set_oplock` function, which maps to `linux_set_kernel_oplock()`. That path goes through the VFS macro `SMB_VFS_LINUX_SETLEASE()`, so VFS modules can audit, replace, or reject lease operations before the default wrapper reaches `linux_setlease()`.

When another local process conflicts with a kernel lease, Linux sends `RT_SIGNAL_LEASE`. The tevent signal callback maps the fd back to Samba’s open file and invokes `break_kernel_oplock()`, which lets the normal SMB oplock break logic notify the client. Release uses the matching `release_oplock` op and clears the Linux lease.

## State And Persistence
The persistent kernel state is the Linux file lease attached to the open fd. Samba-side state is held in `sconn->oplocks.kernel_ops`, `files_struct` records, and the usual share-mode/oplock records managed elsewhere. `linux_setlease()` briefly changes effective privileges with `become_root()`/`unbecome_root()` but restores `errno` and does not persist process identity changes.

The signal handler depends on fd identity remaining findable through `file_find_fd()`. If the fd was already closed, it logs and drops the signal.

## Dependencies And Integration Points
The file depends on Linux `fcntl()` lease operations (`F_SETSIG`, `F_SETLEASE`, `F_GETLEASE`, `F_WRLCK`, `F_UNLCK`), realtime signals, tevent signal integration, Samba file lookup, `break_kernel_oplock()`, VFS lease wrappers, loadparm-controlled kernel oplock initialization, and `struct kernel_oplocks_ops` from Samba headers.

Surrounding integration points include `vfs_default.c` calling `linux_setlease()` from `vfswrap_linux_setlease()`, VFS modules such as GPFS/gluster/audit wrappers overriding `linux_setlease_fn`, and `smb2_service.c` enabling kernel oplocks per share.

## Risks And Edge Cases
Kernel oplocks are platform- and configuration-sensitive. Risks include realtime signal setup failure, support probes that pass on `/dev/null` but fail on a real backing filesystem, fd reuse races if a signal arrives late, lease release failures, and VFS modules returning errors or not implementing the hook. Because `linux_setlease()` becomes root to ensure lease-break signal delivery, privilege bracketing and `errno` preservation are important correctness points.

The handler logs and ignores missing fds; that is safe for late signals but can hide bugs if file tracking is inconsistent. The implementation requests write leases only (`F_WRLCK`), so semantic mapping to SMB oplock types is handled in the higher-level oplock code.

## Test Signals
Build configuration should define `HAVE_KERNEL_OPLOCKS_LINUX` only when `F_SETLEASE` support is detected. Runtime selftest coverage is represented by `source3/selftest/tests.py`, which detects Linux kernel oplock support and schedules `OPLOCK5` and `smb2.kernel-oplocks` when available. Manual or automated tests should verify lease grant/release logging, conflict-triggered signal delivery, interaction with VFS wrappers, and graceful behavior when the kernel or filesystem refuses leases.
