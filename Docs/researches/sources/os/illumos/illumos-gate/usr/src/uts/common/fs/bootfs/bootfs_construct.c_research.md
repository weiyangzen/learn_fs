# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/bootfs/bootfs_construct.c

## Purpose

`bootfs_construct.c` builds the in-memory vnode tree for bootfs from boot-time module metadata stored as properties on the root devinfo node. It also owns the bootfs node cache constructor/destructor and tree teardown.

## File Shape

- Size: 356 lines, 8,675 bytes.
- SHA-256: `57af068dd81b9937b35a73205b51a42f240bad7057ed404a54e2748d613e8349`.
- Defines global `bootfs_node_cache`.
- Key functions: `bootfs_node_constructor()`, `bootfs_node_destructor()`, `bootfs_construct()`, and `bootfs_destruct()`.

## Core Behavior

- Defines template attributes for directories and regular files. Both are read-only/executable mode `0555`, owned by uid/gid 0, with attributes filled in during node initialization.
- `bootfs_node_init()` reinitializes the cached vnode, marks it `VNOSWAP`, assigns vnode ops and filesystem pointer, copies the name, initializes an AVL directory for directory nodes, fills timestamps, fsid, node id, block size, and inserts the node into the filesystem-wide list.
- `bootfs_mkroot()` creates the root directory vnode, sets `VROOT`, points parent to itself, increments directory stats, and publishes the vnode with `vn_exists()`.
- `bootfs_mknode()` creates or reuses directory nodes in the parent AVL tree. Directory name collisions are reused; file collisions return `EEXIST`. File nodes record the physical-memory address and size, update file/byte stats, and set `va_size`/`va_nblocks`.
- `bootfs_construct_entry()` canonicalizes module paths enough to skip leading slashes and `.` components and to honor `..` by walking to the parent, then creates intermediate directories and the final file. Empty names, all-slash names, and trailing slash names are discarded as `EINVAL`.
- `bootfs_construct()` scans `module-addr-%d`, `module-size-%d`, and `module-name-%d` devinfo properties from index 0 upward until any property is missing/zero. It counts invalid paths as discards and duplicate files as duplicates.
- `bootfs_destruct()` removes every node from the filesystem list, asserts only the filesystem's hold remains, releases the vnode, frees the name, and returns the node to the cache.

## Dependencies And Contracts

- Depends on `bootfs_t` and `bootfs_node_t` from `sys/fs/bootfs_impl.h`.
- Uses devinfo root properties populated by early boot/loader handoff.
- Uses AVL trees for per-directory children and a list for all nodes on a mounted bootfs instance.

## Maintenance Notes

Bootfs constructs all nodes at mount time because the boot module set is small and static. Path handling is intentionally simple; it does not create a general-purpose filesystem namespace and preserves "first file wins" behavior for duplicate module names.
