# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_export.c

## Purpose

`nfs_export.c` implements the illumos kernel NFS export registry. It owns per-zone export tables, export creation and removal through `exportfs()`, export lookup by path or filehandle identity, public filehandle state, NFSv4 pseudo-namespace security propagation, export reference lifetime, and helpers that manufacture or resolve NFSv2, NFSv3, and NFSv4 filehandles.

It is the shared export substrate used by the NFS server dispatcher, NFSv2/v3 operation implementations, NFSv4 compound processing, NFS logging, and NFS authorization.

## Main Responsibilities

- Creates per-zone `nfs_export_t` state in `nfs_export_zone_init()`, including the placeholder root/public export, export hash tables, auth cache AVL trees, root vnode binding, and export ID registration.
- Initializes global export state in `nfs_exportinit()`: export ID lock/tree and NFS logging caches.
- Implements `exportfs()` for share, reshare, and unshare operations.
- Maintains export hash links by `{fsid, fid}` and by exported path using `export_link()` and `export_unlink()`.
- Maintains globally unique export IDs in `exi_id_tree`, with overflow-aware duplicate avoidance in `exi_id_get_next()`.
- Copies, frees, adds, removes, and transfers `secinfo_t` security flavor lists, including RPCSEC_GSS mechanism OIDs and root-name lists.
- Propagates NFSv4 security flavor visibility up the pseudo namespace tree with `srv_secinfo_treeclimb()`.
- Maps vnodes to containing export entries through `nfs_vptoexi()`.
- Builds NFSv2, NFSv3, and NFSv4 filehandles through `makefh()`, `makefh3()`, and `makefh4()`.
- Builds WebNFS security-negotiation overloaded filehandles through `makefh_ol()` and `makefh3_ol()`.
- Resolves filehandles back to vnodes through `nfs_fhtovp()`, `nfs3_fhtovp()`, and `nfs4_fhtovp()`.
- Cleans export-dependent NFSv4 state, lock-manager state, auth cache entries, logging buffers, charset conversion caches, visible pseudo-namespace nodes, and vnode references during unexport/free.

## Export Lifecycle

`exportfs()` is the central lifecycle path.

For unshare, it first finds an existing non-root export by path, then calls `unexport()`. `unexport()` unlinks the export under `exported_lock`, removes its export ID from `exi_id_tree`, removes explicitly exported security flavor references from ancestors, either replaces the node with a pseudo export when descendants remain visible or removes the namespace branch, then drops the lock before cleaning NFSv4 state via `rfs4_clean_state_exi()` and notifying the lock manager with `lm_unexport()`.

For share and reshare, `exportfs()`:

1. Copies the requested path from userspace and checks whether that path is already exported.
2. Looks up and traverses the target vnode, including autofs trigger handling via `VOP_ACCESS()` and mounted-vfs traversal.
3. Rejects conflicting attempts to share the same path with a different vnode or the same vnode under a different non-pseudo path.
4. Builds a new `exportinfo_t`, initializes vnode references, auth-cache AVL tables, filehandle template data, export path data, logging path/tag data, and user-supplied security data.
5. Converts non-native data model `secinfo` structures, loads root-name lists, deep-copies RPCSEC_GSS mechanism OIDs, and marks each share-provided flavor as explicitly exported with refcount 1.
6. Installs the RPCSEC_GSS callback when any exported flavor uses RPCSEC_GSS.
7. Loads the WebNFS index option and creates NFS logging buffers when requested.
8. Links the export into the hash tables under `exported_lock`.
9. Replaces an old export for the same vnode when resharing, preserving export IDs and visible pseudo children when needed.
10. Updates the NFSv4 namespace tree with `treeclimb_export()` or by reusing an old tree node.
11. Propagates newly exported security flavors up the ancestor tree.
12. Transfers implicit descendant security references from old export data to new export data for reshare and pseudo-to-real export transitions.
13. Publishes public filehandle state and logs share records when logging is enabled.

The error path is carefully staged with labels `out1` through `out7`, freeing only resources initialized before the failing step.

## Security Flavor Accounting

The file contains a substantial NFSv4 security-flavor reference accounting system. Its goal is to make ancestors and pseudo nodes advertise the union of security flavors needed to reach explicitly exported descendants, while preserving the distinction between flavors explicitly exported on a node and flavors implicitly inherited from descendants.

Key routines:

- `build_seclist_nodups()` condenses an export's flavor list by NFS pseudo flavor number, optionally keeping only explicitly exported flavors.
- `srv_secinfo_add()` increments refcounts for existing flavors and deep-copies new flavors into ancestor or visible-node lists. Pseudo nodes force `M_RO`.
- `srv_secinfo_remove()` decrements explicit flavor refs and removes entries whose refcounts become invalid.
- `srv_secinfo_exp2exp()` handles reshare transfer of descendant flavor refs from an old real export to a new real export.
- `srv_secinfo_exp2pseu()` transfers descendant refs from a removed real export to the pseudo export that replaces it.
- `srv_secinfo_treeclimb()` propagates additions/removals from an export up through `treenode_t` ancestors and their `visible` structures.

This logic is used while holding `exported_lock` as writer and is tightly coupled to the NFSv4 pseudo namespace implementation in nearby files.

## Export Lookup and Filehandle Flow

The export table is hashed by XOR over the filesystem ID and export fid. `checkexport()` looks up an export by `{fsid, xfid}`, maps the placeholder public export to the current real public export, takes an `exi_hold()`, and returns it to NFSv2/v3 callers. `checkexport4()` is the NFSv4 variant: the caller must already hold `exported_lock`, it does not manipulate `exi_count`, and it can additionally require vnode identity to disambiguate lofs/pseudo collisions.

`nfs_vptoexi()` walks from a vnode toward the filesystem or zone root, calling `vop_fid_pseudo()` and `checkexport()` or `checkexport4()` at each step. It supports a `walk` counter used by public filehandle `nosub` checks.

Filehandle creation is version-specific:

- `makefh()` overlays the target file fid into an export template for NFSv2.
- `makefh3()` stores target fid plus export-root fid in an NFSv3 handle, with length bookkeeping for old fixed-size compatibility.
- `makefh4()` uses `vop_fid_pseudo()` and encodes export-root data plus target fid into the fixed NFSv4 filehandle format.
- `makefh_ol()` and `makefh3_ol()` build overloaded WebNFS security-negotiation filehandles containing explicit security flavors in batches.

Filehandle-to-vnode conversion uses the export root vnode's `vfs_t` and `VFS_VGET()`. The NFSv4 path has special handling for pseudo exports through `nfs4_vget_pseudo()` and can return `NFS4ERR_FHEXPIRED` under the optional volatile filehandle test code.

## Public Filehandle and Logging Integration

The per-zone root export starts as a placeholder public filehandle target with `EX_PUBLIC`. A real export with the public option moves `ne->exi_public` to that export and clears the `EX_PUBLIC` bit on the real export so it can be distinguished from the placeholder.

`nfs_getfh()` returns a filehandle to privileged callers, supports NFSv2 and NFSv3 layouts, performs autofs trigger and mounted-vfs traversal, and logs `GETFH` activity when the containing export has `EX_LOG`.

Share and unshare operations call `nfslog_share_record()` and `nfslog_unshare_record()` as appropriate. Export free calls `nfslog_disable()` when a logging buffer is attached.

## Zone and Global Lifetime

Global initialization order is export ID state first, then NFS logging. Per-zone initialization builds the root export before server submodules use it. Shutdown walks all linked exports for the zone and unexports every non-root export. Zone finalization removes the root export from the hash and export-ID tree, destroys root auth caches and locks, verifies no export IDs remain for the zone, destroys `exported_lock`, and frees `nfs_export_t`.

## Dependencies and Integration Points

- NFS server globals from `nfs_server.c` via `nfs_srv_getzg()`.
- NFSv4 namespace helpers: `treeclimb_export()`, `treeclimb_unexport()`, `tree_update_change()`, `pseudo_exportfs()`, `free_visible()`.
- NFSv4 state cleanup: `rfs4_clean_state_exi()`.
- Authorization cache: `nfsauth_cache_free()`, AVL auth cache setup.
- Security service helpers: `sec_svc_loadrootnames()`, `sec_svc_freerootnames()`, `sec_svc_control()`, RPCSEC_GSS callback registration.
- Lock manager: `lm_unexport()`.
- NFS logging: `nfslog_init()`, `nfslog_setup()`, `nfslog_disable()`, share/unshare/getfh logging.
- VFS/vnode operations: `lookupname()`, `VOP_FID()`, `vop_fid_pseudo()`, `VFS_VGET()`, `traverse()`, vnode holds/releases.
- Zone infrastructure for root vnode and shutdown credentials.

## Concurrency and Locking Notes

`nfs_export_t.exported_lock` serializes export table and namespace-tree mutations. Readers use it for export lookup by path or filehandle. `nfs_exi_id_lock` separately protects export ID allocation and `exi_id_tree`. Each `exportinfo_t` has `exi_lock` for `exi_count`, and auth-cache tables have `exi_cache_lock`.

Several routines require specific lock context: `srv_secinfo_treeclimb()`, `export_link()`, and `export_unlink()` assert writer ownership of `exported_lock`; `checkexport4()` asserts the lock is already held; `exi_id_get_next()` asserts `nfs_exi_id_lock`.

## Risks and Edge Cases

- Security-flavor reference transfer during reshare/unshare is subtle. Incorrect refcount transfer can advertise wrong NFSv4 `SECINFO` data for pseudo paths.
- `exportfs()` has many partially initialized resources; future changes need to preserve the staged unwind ordering.
- `nfs_vptoexi()` walks parents using `".."`; unusual filesystem behavior or fid failures map to export lookup failure.
- Vnode identity is needed in NFSv4 export lookup because lofs and pseudo nodes may share fsid/fid identity with real nodes.
- NFSv3 filehandle copyout preserves old padding behavior for compatibility, while logging may require a downsized old handle format.
- Public filehandle state is global per zone and interacts with share/unshare logging and WebNFS multicomponent lookup.
- Optional `VOLATILE_FH_TEST` code is explicitly test-oriented and notes incomplete locking/design assumptions.

## Testing and Verification Signals

Useful tests cover share, reshare, unshare, public export changes, pseudo export creation/removal, descendant security flavor propagation, RPCSEC_GSS root-name and mechanism handling, NFSv2/v3/v4 filehandle round trips, lofs/pseudo export disambiguation, WebNFS security-negotiation overloaded filehandles, logging-enabled exports, zone shutdown cleanup, and NFSv4 state cleanup on unexport.
