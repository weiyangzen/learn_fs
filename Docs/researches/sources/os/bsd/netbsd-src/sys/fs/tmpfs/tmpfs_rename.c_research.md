# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_rename.c

Read completely: 591 lines.

This implements tmpfs rename through NetBSD’s `genfs_sane_rename`/`genfs_insane_rename` framework. The file provides callbacks for directory-empty checks, rename/remove possible and permitted checks, actual rename/remove mutations, lookup, genealogy analysis, and directory locking.

The actual rename path preallocates a new target name when needed, moves the source dirent between directories, removes/replaces an existing target, updates dirent names, adjusts directory parent/link relationships, updates ctime/mtime on affected nodes, and purges rename cache entries. Genealogy walks parent links from target directory upward to prevent illegal directory cycles and handles directories concurrently removed by rmdir.

Important interactions: delegates policy checks to genfs UFS-like helpers using tmpfs flags, modes, and ownership. Uses `tmpfs_dir_attach`, `tmpfs_dir_detach`, `tmpfs_free_dirent`, `tmpfs_strname_alloc`, and vnode cache lookup.

Security/reliability notes: the implementation is assertion-heavy and explicitly verifies lock state and same-mount invariants. Early name allocation avoids unrecoverable ENOSPC after structural changes have started.
