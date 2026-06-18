# File Research: sources/os/linux/linux-stable/fs/init.c

This file provides init-only wrappers that mimic filesystem syscalls without using user address space path pointers or regular syscall file descriptor entry points. It is used by early init and related kernel startup code.

Key responsibilities:
- Implements init-time mount namespace operations: `init_mount()`, `init_umount()`, and `init_pivot_root()`.
- Implements current-root and current-working-directory changes through `init_chdir()` and `init_chroot()`.
- Provides init-time metadata operations: `init_chown()`, `init_chmod()`, `init_eaccess()`, `init_stat()`, and `init_utimes()`.
- Provides init-time creation/removal helpers: `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, and `init_rmdir()`.
- Provides `init_dup()` to allocate a file descriptor for an existing kernel `struct file`.

Important interactions:
- Uses `kern_path()` for kernel-space pathname lookup.
- Calls internal VFS helpers declared in `fs/internal.h`, including `path_mount()`, `path_umount()`, `path_pivot_root()`, `filename_*at()` helpers, `chmod_common()`, and `chown_common()`.
- Checks permissions and security hooks for `chdir`, `chroot`, and write-intent operations.
- Uses `CLASS(filename_kernel, ...)` cleanup wrappers for kernel pathname objects.

Notable invariants and risks:
- Functions are marked `__init`, so they are intended only for boot/init lifecycle.
- These helpers intentionally avoid normal syscall user-copy paths.
- `init_chroot()` still enforces `CAP_SYS_CHROOT` and `security_path_chroot()`.

Research notes:
- This is a compact but important early-boot adapter layer between init code and normal VFS internals.
