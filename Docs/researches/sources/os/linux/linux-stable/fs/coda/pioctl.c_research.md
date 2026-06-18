# File Research: sources/os/linux/linux-stable/fs/coda/pioctl.c

This file implements Coda pioctl handling, exposing a special ioctl endpoint for Coda control operations routed to Venus.

Key responsibilities:
- Defines `coda_ioctl_inode_operations` and `coda_ioctl_operations`.
- Rejects execute permission on the pioctl inode through `coda_ioctl_permission()`.
- Implements `coda_pioctl()` to copy `PioctlData` from userspace, resolve the userspace path, ensure the target inode belongs to the same Coda superblock, and forward the operation to `venus_pioctl()`.

Important control flow:
- `copy_from_user()` reads ioctl arguments.
- `user_path_at()` resolves `data.path`, honoring `data.follow`.
- The target inode’s superblock must match the ioctl inode’s superblock.
- The target inode’s Coda fid is passed to Venus with the ioctl command and pioctl data.

Dependencies:
- Relies on `venus_pioctl()` from `upcall.c`.
- Relies on `ITOC()`/Coda inode private state for target fid extraction.

Risks and invariants:
- Cross-filesystem pioctl targets are rejected with `-EINVAL`.
- Userspace path handling is delegated to VFS lookup, including follow behavior.
- Bad userspace argument copying returns `-EINVAL`, not `-EFAULT`, matching the local convention in this file.
