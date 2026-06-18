# File Research: sources/os/linux/linux-stable/fs/ocfs2/Makefile

Purpose: Build rules for OCFS2 core objects, stack glue, optional clustering stacks, and subdirectories.

Key contents:
- Adds local include path with `ccflags-y := -I$(src)`.
- Builds `ocfs2.o` and `ocfs2_stackglue.o` when `CONFIG_OCFS2_FS` is enabled.
- Builds `ocfs2_stack_o2cb.o` under `CONFIG_OCFS2_FS_O2CB`.
- Builds `ocfs2_stack_user.o` under `CONFIG_OCFS2_FS_USERSPACE_CLUSTER`.
- Defines the large `ocfs2-objs` aggregate, including allocation, aops, block checks, buffer I/O, dcache, directories, DLM glue, export, extent map, file, heartbeat, inode, ioctl, journal, localalloc, locks, mmap, namei, refcount tree, reservations, move extents, resize, slot map, suballoc, super, symlink, sysfile, uptodate, local/global quota, xattr, ACL, and filecheck objects.
- Descends into `dlmfs/` and `cluster/` for `CONFIG_OCFS2_FS`; descends into `dlm/` for O2CB.

Important invariants:
- `cluster/` is always built with OCFS2 for masklog support.
- `acl.o` and `xattr.o` are part of the main OCFS2 object when the filesystem is enabled.
