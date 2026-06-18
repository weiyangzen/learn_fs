# File Research: sources/os/linux/linux/fs/init.c

Early-init filesystem syscall substitutes. These helpers let `init/` and related kernel boot code perform filesystem operations without using user address spaces or normal file-descriptor syscall entry.

Provided helpers:
- Mount namespace operations: `init_mount()`, `init_umount()`, `init_pivot_root()`.
- Directory/root changes: `init_chdir()`, `init_chroot()`.
- Metadata operations: `init_chown()`, `init_chmod()`, `init_stat()`, `init_eaccess()`, `init_utimes()`.
- Object operations: `init_mknod()`, `init_link()`, `init_symlink()`, `init_unlink()`, `init_mkdir()`, `init_rmdir()`.
- `init_dup()` installs a kernel-held file into a new fd slot.

Implementation pattern:
- Path-based helpers use `kern_path()` and release with `path_put()`.
- Write operations acquire mount write access when needed.
- Name-based create/remove operations use `CLASS(filename_kernel, ...)` wrappers before calling internal filename helpers.
- `init_chroot()` checks execute permission, `CAP_SYS_CHROOT`, and LSM `security_path_chroot()`.

Risks:
- These functions run during early boot, so they bypass normal user-copy syscall plumbing but still need correct VFS permission, capability, LSM, and mount-write semantics.
- `init_dup()` returns `0` after installing the fd rather than the fd number, matching this internal API’s expected use.
