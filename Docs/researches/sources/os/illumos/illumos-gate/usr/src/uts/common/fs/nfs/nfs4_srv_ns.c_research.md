# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_ns.c

Implements the NFSv4 server pseudo-filesystem namespace. It builds, merges, tears down, and queries pseudo export nodes and visible directory lists so NFSv4 clients can traverse unexported path components to reach real exported descendants.

Key elements:
- Pseudo fid support:
  - `vop_fid_pseudo()` calls `VOP_FID()` but substitutes `va_nodeid` when remote NFS fids are unsupported or too large for NFSv4 export filehandle templates.
  - `nfs4_vget_pseudo()` resolves a fid against an export's visible list or export root vnode and returns a held vnode.
- Pseudo export creation: `pseudo_exportfs()` allocates an `exportinfo`, fills fsid/fid/vnode/template filehandle, marks `EX_PSEUDO`, appends `" (pseudo)"` to the path, copies propagated security flavor information, initializes auth cache AVL tables, links the export, and assigns an export id.
- Visible-list cleanup: `free_visible()` releases visible vnodes, security info lists, and visible entries.
- Namespace tree primitives:
  - `tree_add_child()` links a child at the front of a parent's child list.
  - `tree_find_child_by_vis()` finds a direct child with the same `exp_visible_t` pointer.
  - `tree_prepend_node()` creates a new tree node, optionally links an existing subtree below it, attaches a visible entry, and attaches an exportinfo.
  - `tree_remove_node()` unlinks and frees a tree node, including root-node handling.
- Visible-list merge: `more_visible()` merges a newly constructed visible path/tree into an existing root or pseudo export. It increments `vis_count` for shared path components, transfers `vis_exported` and exportinfo pointers when safe, appends new visible entries, adds new tree branches, and updates namespace change timestamps.
- Visible-list reduction: `less_visible()` decrements one visible entry's reference count from an exportinfo visible list and removes/frees it when the count reaches zero.
- Export climb: `treeclimb_export()` walks from a new real export up toward the zone root, crossing mountpoints with `untraverse()`, building visible entries and tree nodes for path components, creating pseudo exports for unexported filesystem roots, merging into existing exports when found, installing `ne->ns_root`, and cleaning up partially built exports/visibles/tree nodes on error.
- Unexport climb: `treeclimb_unexport()` clears the unshared export's tree link, marks its visible entry non-exported, walks upward to release pseudo exports with no children, release parent visible entries, delete non-exported leaf nodes, and update change timestamps.
- Mountpoint reverse traversal: `untraverse()` walks from a VROOT or zone-root vnode back across mounted-on vnodes using `vfs_lock_wait()`, vnode holds, and releases.
- Namespace queries:
  - `get_root_export()` climbs a tree node's parents to return the filesystem root exportinfo for a descendant export.
  - `has_visible()` reports whether a vnode has exported descendants visible through the pseudo namespace.
  - `nfs_visible()` checks whether a vnode is visible in an export and returns whether the visible path component is itself an exported node.
  - `nfs_exported()` checks whether a vnode is an export root or a visible entry marked exported.
  - `nfs_visible_inode()` checks visibility by inode number for READDIR filtering and returns the matching visible entry.
  - `nfs_visible_change()` returns pseudo-namespace change timestamps for export roots or visible entries.
  - `tree_update_change()` updates either `ne->ns_root_change` or a treenode visible entry's `vis_change`.

Dependencies:
- NFS export structures: `nfs_export_t`, `exportinfo_t`, `exp_visible_t`, `treenode_t`, `export_link()`, `export_unlink()`, `exi_rele()`, `checkexport4()`, `exi_id_get_next()`, `exi_id_tree`.
- Vnode/VFS APIs: `VOP_FID`, `VOP_GETATTR`, `VOP_LOOKUP`, `VN_HOLD`, `VN_RELE`, `VN_CMP`, `VROOT`, `vfs_lock_wait`, `vfs_unlock`, `vfs_vnodecovered`.
- Export security helpers: `srv_secinfo_exp2pseu()`, `srv_secinfo_list_free()`, auth cache AVL initialization and comparison.
- Zone/root helpers: `VN_IS_CURZONEROOT`, `EXI_TO_ZONEROOTVP`, current zone id checks, per-zone export root.
- Namespace comparison macros: `EQFID`, `EQFSID`, `PSEUDO`, `TREE_ROOT`, `TREE_EXPORTED`, `vis2exi`.

Research notes:
- The pseudo namespace is represented twice: linked `exp_visible` lists attached to exportinfo roots and a tree of `treenode_t` objects. The two are kept connected by pointers but can have different lengths during merge scenarios.
- `vis_count` is the key lifetime mechanism for shared path components; unexport must decrement visible counts even when tree node deletion stops at a still-used branch.
- The implementation has explicit LOFS safeguards: several query paths compare fid/fsid after vnode comparison because `VN_CMP()` can miss LOFS-equivalent nodes.
- Change attributes for pseudo namespace entries are maintained independently of filesystem ctime and are consumed by attribute and READDIR code to make namespace changes visible to NFSv4 clients.
- Error handling in `treeclimb_export()` is nontrivial because partially allocated pseudo exports may own visible lists also referenced from tree nodes; cleanup intentionally frees through exportinfo where possible to avoid double frees.
