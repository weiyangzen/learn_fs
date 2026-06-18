# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/export.c

## Purpose

`export.c` implements Gluster FSAL export operations and export creation. It maps NFS export paths to Gluster volume paths, creates FSAL handles from GFAPI handles, reports dynamic filesystem stats, allocates per-state fd containers, manages shared `glusterfs_fs` volume objects, configures GFAPI/upcalls, and enables pNFS MDS/DS support. The complete 832-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `export_release`, `lookup_path`, `wire_to_host`, `create_handle`, `glfs2fsal_handle`, `get_dynamic_info`, `gluster_free_state`, `glusterfs_alloc_state`, `fs_supported_attrs`, `get_fsal_obj_hdl`, `export_ops_init`, `glusterfs_free_fs`, `glusterfs_get_fs`, and `glusterfs_create_export`. Important config/state types are `struct glexport_params`, `enum transport`, `struct glusterfs_export`, and `struct glusterfs_fs`.

## Control Flow

Export release detaches the export, frees ops, decrements the shared Gluster volume object, and frees export strings. `lookup_path` translates the NFS mount path into a Gluster volume-relative path, looks up a GFAPI object, extracts its handle and volume UUID, and constructs a Ganesha FSAL handle. `create_handle` reverses a wire handle by extracting the GFAPI object handle from the second half of the digest. `glusterfs_get_fs` reuses an existing volume object by volume name or creates a new GFAPI context, sets volfile server/logging, initializes it, and registers or starts upcall handling. `glusterfs_create_export` parses config, initializes export ops, attaches the export, stores path/credential state, and enables pNFS DS/MDS registration when supported.

## State and Persistence Behavior

Shared volume state is kept in `GlusterFS.fs_obj` under `GlusterFS.glfs_lock` with a refcount and `destroy_mode`. Runtime export state stores mount path, volume export path, saved uid/gid, security-label xattr, and pNFS flags. Persistent effects are only indirect through GFAPI; this file primarily manages client connection lifetime, upcall registration, and pNFS DS registry entries.

## Dependencies and Integration Points

Dependencies include GFAPI (`glfs_new`, `glfs_set_volfile_server`, `glfs_set_logging`, `glfs_init`, `glfs_h_*`, `glfs_statvfs`, upcall register/unregister), Ganesha config parsing, FSAL export/state APIs, Gluster internal handle construction, pNFS utilities, export manager, LTTng tracepoints, and optional old polling-thread upcalls. It integrates with `fsal_up.c`, `ds.c`, and Gluster MDS pNFS code.

## Risks and Edge Cases

Volume reuse keys only on volume name, not hostname, transport, volpath, or log path, so two exports with the same volume name but different connection parameters may unexpectedly share a GFAPI context. `lookup_path` string translation has symlink and prefix TODOs and must handle root export path specially. Error cleanup in `glusterfs_get_fs` calls `glist_del` on a freshly initialized object in an error path, which should be reviewed. Upcall thread/register cleanup must avoid races with destroy mode and export release. pNFS DS insertion can fail on server id collision after export attach.

## Test Signals

Useful tests include multiple exports of one volume, conflicting same-volume config, path lookup for root and subdirectory exports, wire handle length validation, statvfs mapping, export release with active upcall thread, upcall register/unregister failures, GFAPI init failure cleanup, pNFS DS server-id collision, pNFS MDS/DS enabled and disabled exports, ACL support mask behavior, and leak/race tests around shared `glusterfs_fs` refcounts.
