# File Research: sources/os/linux/linux/fs/hostfs/hostfs.h

Purpose: Defines the ABI between UML kernel hostfs code and host-side syscall wrapper code.

Key definitions:
- `struct hostfs_timespec`, `struct hostfs_iattr`, and `struct hostfs_stat` mirror metadata passed across the hostfs boundary.
- Declares wrapper functions for stat/access/open/read/write/fsync, directory iteration, creation/removal/linking/renaming, symlink read/write, attribute updates, special node creation, and statfs.

Dependencies and integration:
- Includes UML OS and generated asm-offset headers.
- Implemented by `hostfs_user.c`, exported by `hostfs_user_exp.c`, and consumed by `hostfs_kern.c`.

Risk notes:
- This is an internal ABI; field sizes and signedness must stay compatible between kernel UML code and user syscall wrappers.
