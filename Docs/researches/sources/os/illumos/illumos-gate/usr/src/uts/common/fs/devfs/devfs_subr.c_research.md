# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/devfs/devfs_subr.c

This file contains the main support routines for illumos `devfs`, the filesystem mounted at `/devices`. It manages `dv_node` allocation, device-tree-backed lookup, shadow permission storage, directory population, cleanup, stale-node handling, and tree walking.

Core responsibilities:
- Creates and destroys the `dv_node_cache`.
- Builds root, directory, and leaf device nodes.
- Maintains per-directory AVL trees of child `dv_node` entries.
- Derives stable inode numbers from devinfo nodes and device numbers.
- Creates and finds shadow attribute nodes in the underlying filesystem.
- Drives top-down device-tree configuration during lookup and readdir.
- Cleans cached devfs nodes during device removal or DR operations.
- Supports permission reset and stale shadow cleanup after driver removal.

Important operations:
- `dv_node_cache_init` and `dv_node_cache_fini` create/destroy the cache and `devfs_clean_key` TSD key.
- `dv_mkino` derives 32-bit-compatible inode numbers for directories and leaf nodes, including VCHR/VBLK differentiation.
- `dv_mkroot` constructs the root `dv_node`, sets VROOT, initializes `dv_entries`, and records `ddi_root_node()`.
- `dv_mkdir` creates directory nodes for attached devinfo nodes and holds the devinfo node.
- `dv_mknod` creates VCHR/VBLK leaf nodes from `ddi_minor_data`, records internal/no-fs-permission/default-mode flags, and holds private policy data where present.
- `dv_destroy` frees unreferenced nodes, releases shadow vnodes, attributes, names, devinfo holds, and private policy data. Referenced stale directories are left for `devfs_inactive`.
- `dv_findbyname`, `dv_insert`, and `dv_unlink` manage the directory AVL tree and link counts.
- `dv_vattr_merge` overwrites nodeid/link/fsid/rdev/type details so backing-store attributes look like devfs attributes.
- `devfs_get_defattr` computes default permissions from directory defaults, `DM_NO_FSPERM`, `minor_perm`, or private minor defaults.
- `dv_shadow_node` finds or creates the backing attribute vnode for a devfs node, handles read-only fallback to memory attributes, and tracks non-trivial ACLs.
- `dv_find_leafnode` locates a named minor under an attached devinfo node.
- `dv_clone_mknod` manufactures clone-device nodes for STREAMS drivers.
- `dv_find` is the central lookup engine: handles `.`, `..`, cached children, shadow-node construction, device-tree configuration through `ndi_devi_config_one`, alias handling, hidden-node filtering, clone/minor node creation, duplicate-race handling, internal-node filtering, and specfs vnode substitution for VCHR/VBLK leaves.
- `dv_filldir` populates a directory by configuring children, iterating attached child devinfo nodes and their minor data, and creating both leaf minor nodes and child directories.
- `dv_cleandir` recursively removes cached children, marks directories stale under force-clean rules, and sets `DV_BUILD` so future reads rebuild.
- `dv_reset_perm_dir` and `devfs_reset_perm` walk cached nodes and update memory permissions to match `minor_perm` defaults when no explicit shadow override exists.
- `devfs_remdrv_cleanup` and `devfs_remdrv_rmdir` remove stale shadow-permission files for removed drivers.
- `dv_walk` walks cached `dv_node` subtrees and invokes a callback.

Locking and cleanup model:
- Per-node contents are protected by `dv_contents`.
- `devfs_clean_key` marks cleanup paths that must avoid blocking in places that could deadlock against device-tree configuration.
- `dv_find` uses `dv_busy` while dropping locks for device-tree operations so forced cleanup can identify active construction.
- `dv_cleandir` returns `EBUSY` internally for lock or reference conflicts, but higher-level `devfs_clean` treats cleanup as best effort.

Research notes:
- `dv_find` is the highest-value function for understanding `/devices` lookup side effects.
- `dv_shadow_node` is the key bridge between synthetic devfs nodes and persistent filesystem permissions.
- `dv_cleandir` is central to hotplug, detach, and dynamic reconfiguration behavior.
