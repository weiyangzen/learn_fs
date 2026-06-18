# File Research: sources/os/linux/linux-stable/fs/overlayfs/inode.c

## Scope

This file implements overlayfs inode operations and inode lifecycle: setattr, getattr/stat inode mapping, permission checks, symlink targets, POSIX ACL get/set with idmapped layers, timestamp updates, fiemap, fileattr get/set including protected immutable/append flags, inode operation tables, lockdep class annotation for nested overlays, inode number mapping, inode initialization, nlink xattr accounting, inode hashing/lookup/trap inodes, and overlay inode creation.

## Public And Internal APIs Covered

- VFS inode operations: `ovl_setattr()`, `ovl_getattr()`, `ovl_permission()`, `ovl_update_time()`, `ovl_fileattr_get()`, `ovl_fileattr_set()`, and symlink `ovl_get_link()`.
- ACL APIs under `CONFIG_FS_POSIX_ACL`: `ovl_get_acl_path()`, `do_ovl_get_acl()`, `ovl_set_acl()`.
- Fileattr helpers: `ovl_real_fileattr_get()`, `ovl_real_fileattr_set()`.
- Inode setup: `ovl_new_inode()`, `ovl_inode_init()`, `ovl_get_inode()`, `ovl_lookup_inode()`, `ovl_get_trap_inode()`, `ovl_lookup_trap_inode()`.
- Nlink helpers: `ovl_set_nlink_upper()`, `ovl_set_nlink_lower()`, `ovl_get_nlink()`.
- Operation tables: regular file, symlink, special inode ops, and overlay address-space ops.

## Control Flow And Behavior

- `ovl_setattr()` validates attributes on the overlay inode, chooses metadata-only or data copy-up for size changes, strips unsupported `ATTR_FILE` and `ATTR_OPEN`, gets write access for truncation, applies changes to the upper dentry under mounter credentials, and copies attrs back to the overlay inode.
- `ovl_getattr()` obtains real stats, overlays effective immutable/append statx flags, preserves stable st_dev/st_ino across copy-up when possible, handles origin/index semantics, fixes metacopy block reporting, maps inode numbers through samefs/xino/pseudo-dev rules, sets merge-dir nlink to 1, and reports overlay nlink for indexed upper files.
- Permission checking first applies generic permission against the overlay inode with task credentials, then checks underlying real inode permissions with mounter credentials. Lower write checks are converted to read checks when copy-up would be needed.
- Symlink reads delegate to the real dentry under overlay credentials.
- ACL retrieval can clone and idmap ACL entries from idmapped lower/upper mounts so cached ACLs on underlying filesystems are not mutated. RCU ACL lookup drops out for idmapped mounts.
- ACL setting copies up lower objects when necessary, checks owner/capability rules, handles SGID stripping through `ovl_setattr()`, and sets or removes ACL xattrs on the real upper object.
- Atime updates touch the upper path only when present and copy the resulting atime to the overlay inode.
- Fiemap delegates to the real data inode.
- Fileattr set copies up, writes protected immutable/append state to overlay private xattrs, applies fileattr to upper, merges real flags with protected overlay flags, and refreshes ctime. Fileattr get reads real attributes and overlays protected flags.
- Inode initialization copies attrs/flags from real inode, maps inode numbers, installs operation tables by mode, marks ACLs uncached, sets `S_NOCMTIME`, and annotates locks based on overlay stack depth.
- Indexed nlink xattrs store union nlink deltas relative to upper or lower inode nlink using `U+N` / `L+N` text encoding.
- `ovl_get_inode()` decides whether to hash by upper or lower inode, reuses cached inodes after strict verification, creates anonymous inodes for lower hardlinks that will be broken on copy-up, initializes flags such as index/const-ino/whiteouts/impure, and checks protected fileattr xattrs.

## State And Data Structures

- Overlay inode private data tracks upper dentry, lower stack entry, redirects, lowerdata redirect, flags, and lock.
- Inode number mapping uses overlay `last_ino`, samefs detection, xino high bits, layer fsid, and pseudo-devs.
- Trap inodes are dead directory inodes keyed by layer root real inode to detect lookup loops/conflicting layer roots.
- Protected fileattr flags are represented both in overlay inode `i_flags` and overlay private xattrs.

## Dependencies

- Depends on overlayfs path/type helpers, copy-up, xattrs, origin/index verification, credentials, nlink helpers, lowerdata path resolution, and directory/file operation tables from sibling files.
- Uses VFS permission, stat, ACL, fileattr, fiemap, inode hash, lockdep, idmapped mount, and security ioctl hooks.

## Risks And Invariants

- st_dev/st_ino mapping must remain stable across copy-up when possible while avoiding collisions across layers.
- Overlay permission semantics intentionally combine caller authorization on overlay inode with mounter authorization on underlying inode.
- ACL idmapping must clone before rewriting entries to avoid corrupting underlying filesystem-wide ACL cache.
- Inode cache reuse requires verifying stored upper/lower real inodes against lookup dentries, especially for directories and NFS decode paths.
- Nested overlay lock classes must reflect stack depth to keep lockdep from reporting false recursive inode-lock cycles while still catching real inversions.
