# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/main.c

## Purpose

`main.c` implements Ceph FSAL module registration, module/export configuration parsing, shared libcephfs mount creation/reuse, root handle initialization, delegation/reclaim support, libcephfs cache callbacks, optional Ceph service registration, and module teardown. The complete 1150-line file was read for this report.

## Important APIs, Types, and Functions

Important items include global `CephFSM`, `ceph_conf_commit`, `init_config`, `find_cephfs_root`, `ceph_export_commit`, export config tables, `enable_delegations`, `handle_deleg_transition`, `create_unique_id`, `reclaim_reset`, `node_takeover_reclaim`, `select_filesystem`, callback functions `ino_release_cb`, `ino_invalidate_cb`, `dentry_invalidate_cb`, `umask_cb`, `register_callbacks`, `create_export`, `ceph_register_nfs_service`, `MODULE_INIT init`, and `MODULE_FINI finish`.

## Control Flow

Module init registers FSAL `Ceph`, initializes the mount AVL tree, installs module ops, and initializes object ops. Configuration parsing loads module flags and rejects incompatible `client_oc` plus `zerocopy`. Export creation parses FSAL block parameters, builds a mount key, reuses an existing `ceph_mount` or creates a new libcephfs client, reads Ceph config, sets key and client options, initializes/mounts/selects filesystem, registers callbacks, performs reclaim reset, finds the export root, constructs the root handle, attaches the export, and enables delegation timeout when configured. Error paths unwind in reverse under `cmount_lock`.

## State and Persistence Behavior

Global module state persists for the module lifetime. Shared `ceph_mount` objects persist while at least one export references the same filesystem/mount/user/secret key. Reclaim support creates stable Ceph client UUIDs from node id and either export id or a CityHash over node/user/filesystem/mount path, then starts/finishes reclaim with libcephfs. Callback registration connects Ceph MDS cache invalidation/release events to Ganesha upcall vectors.

## Dependencies and Integration Points

Dependencies include Ganesha FSAL registration, config parsing, export manager, NFS recovery/grace APIs, CityHash, libcephfs session/config/mount/callback/delegation/reclaim APIs, dynamic loader support for `libganesha_rados_urls.so`, and object/export ops from other Ceph FSAL files. It integrates with runtime export option changes through `handle_deleg_transition`.

## Risks and Edge Cases

Mount sharing is protected by `cmount_lock`, but create error handling manipulates export lists and refcounts before all fields are fully initialized. `select_filesystem` has a fallback branch that appears to reference `cm->fs_name` rather than `cm->cm_fs_name`, a likely compile issue when named-filesystem support is absent. Service registration exits the process if the RADOS URL library cannot be loaded while `register_service` is true. Delegation timeout must stay below Ceph MDS session timeout to avoid blacklist risk. Reclaim UUID changes can affect state recovery compatibility.

## Test Signals

Useful tests include module config parsing, incompatible flag rejection, export config validation for `cmount_path`, shared mount reuse and teardown, failed `ceph_create`/config/init/mount/select/reclaim paths, root lookup for mounted root and subdirectories, callback-driven invalidate/release upcalls, delegation option transitions at runtime, reclaim reset and node takeover across multiple mounts, service registration missing-library handling, and module unload after all exports release.
