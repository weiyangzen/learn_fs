# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_pseudo.c

## Purpose
Manages the NFSv4 pseudo filesystem export tree. It mounts exports at pseudopath junctions, creates intermediate pseudo directories, unmounts exports and cleans unused pseudo nodes, and prunes/remounts subtrees during export configuration updates.

## Important APIs, Types, and Functions
- `struct pseudofs_state` carries the export being mounted, current pseudo object, and refcounted pseudopath/fullpath strings.
- `is_export_pseudo` detects PSEUDO and MDCACHE-on-PSEUDO exports.
- `cleanup_pseudofs_node` recursively removes empty pseudo directories after unmount.
- `make_pseudofs_node` looks up or creates a pseudo directory path component.
- `pseudo_mount_export` builds a mount path, records junction object/parent export, and sets `junction_export`.
- `create_pseudofs` processes the export mount work queue under a root op context.
- `pseudo_unmount_export`, `pseudo_unmount_export_tree`, and `prune_pseudofs_subtree` detach exports and descendants.

## Control Flow
Mounting skips non-v4 exports and the pseudo root, snapshots pseudopath/fullpath with RCU/refstrs, finds the parent export for the pseudopath prefix, gets the parent root object, walks remaining path components using `make_pseudofs_node`, then under export locks records mounted-on fileid, junction object refs, parent export refs, and parent mounted-export list membership. It sets `export->is_mounted` and only then writes `state_hdl->dir.junction_export` and `jct_pseudopath` under the junction lock, making the junction visible.

Unmounting locks the export, detaches junction metadata, clears export junction/parent fields, removes the mounted-export list node, clears `is_mounted`, initializes an op context for the parent export, either removes unused PSEUDO FS nodes recursively or calls the parent FSAL `unmount`, then releases export/object/refstr refs. Pruning walks descendants depth-first under export list locks, unmounts defunct or flagged subtrees, and queues eligible exports for remount.

## State and Persistence Behavior
Mutates in-memory export graph state (`exp_junction_obj`, `exp_parent_exp`, `mounted_exports_list`, `is_mounted`, `exp_mounted_on_file_id`, update flags) and pseudo FSAL namespace directories. It also mutates junction fields inside object state handles. It relies on the export admin mutex externally for update serialization.

## Dependencies and Integration Points
Depends on export manager work queues and lookups, FSAL lookup/create/remove/lookupp/unmount operations, object refs, export refs, RCU refstrs, op context initialization/release, PSEUDO and MDCACHE FSAL naming conventions, and junction traversal consumers such as LOOKUP/READDIR/SECINFO.

## Risks
Refcount and lock ordering are complex: export locks, parent export locks, junction locks, RCU refstr refs, object LRU/active/root refs, and op context export refs all interact. `cleanup_pseudofs_node` edits the path string in place and assumes it will not walk past pseudo root. `make_pseudofs_node` treats any PSEUDO lookup error as create-needed during updates. Junction visibility depends on setting `junction_export` last.

## Test Signals
Test mounting root and nested exports, creating missing pseudo directories, existing non-directory path component failure, non-PSEUDO parent create failure, export update prune/remount, unmount of leaf and subtree exports, cleanup of now-empty pseudo directories, mounted-on non-PSEUDO unmount callback, READDIR/LOOKUP junction visibility after mount, and refcount/leak checks across repeated reloads.
