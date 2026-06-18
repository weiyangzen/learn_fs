# File Research: sources/os/linux/linux/fs/ocfs2/Makefile

## Role

Defines how OCFS2 and its cluster stack components are built.

## Major Contents

- Adds `-I$(src)` to compile flags.
- Builds main objects when `CONFIG_OCFS2_FS` is enabled:
  - `ocfs2.o`
  - `ocfs2_stackglue.o`
- Builds cluster stack modules conditionally:
  - `ocfs2_stack_o2cb.o` for `CONFIG_OCFS2_FS_O2CB`
  - `ocfs2_stack_user.o` for `CONFIG_OCFS2_FS_USERSPACE_CLUSTER`
- `ocfs2-objs` aggregates the main filesystem implementation:
  - Allocation, address-space ops, block checks, buffer-head I/O, dcache, directory, DLM glue, export, extent map, file, heartbeat, inode, ioctl, journal, localalloc, locks, mmap, namei, refcount tree, reservations, move extents, resize, slot map, suballoc, super, symlink, sysfile, uptodate, quota, xattr, ACL, and filecheck objects.
- Adds subdirectories:
  - `dlmfs/`
  - `cluster/`
  - `dlm/` when O2CB is enabled.

## Important Invariants

- `acl.o` is part of the main `ocfs2.o` object list.
- `cluster/` is always built with OCFS2 for masklog support.
- `dlm/` is tied to O2CB kernelspace clustering.

## Dependencies

- Linux kernel kbuild.
- The listed `.o` files correspond to OCFS2 source modules in the same directory and subdirectories.

## Notes For Future Work

- The object list makes clear that ACL support is not isolated as an optional object once OCFS2 is enabled.
- Formatting is legacy kbuild style with tabs/backslash continuations.
