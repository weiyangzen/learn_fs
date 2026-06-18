# sources/user-network-fs/samba/source3/modules/vfs_glusterfs_fuse.c

Purpose: implements the stackable `glusterfs_fuse` helper module for shares that access Gluster through a local FUSE mount. It preserves Gluster-specific case-insensitive name lookup and stabilizes Samba file IDs across local FUSE device numbers.

Important APIs/types/functions: `vfs_gluster_fuse_get_real_filename_at()` queries the `glusterfs.get_real_filename:<name>` xattr on a directory to resolve actual case. `struct vfs_glusterfs_fuse_handle_data` caches mappings from local `st_dev` values to synthetic 64-bit device IDs. `vfs_glusterfs_fuse_load_devices()` scans `/etc/mtab`, stats mount directories, strips any host prefix from `mnt_fsname`, and hashes the remaining filesystem name with `vfs_glusterfs_fuse_uint64_hash()`. `vfs_glusterfs_fuse_file_id_create()` delegates to the next module, then replaces `id.devid` when a mapping is found.

Control flow: on connect the module calls `SMB_VFS_NEXT_CONNECT()`, allocates handle data, preloads the mount-device cache, and stores it on the VFS handle. File ID creation first uses the default downstream ID, then lazily reloads `/etc/mtab` if the device was not cached. Real-name lookup opens `"."` relative to the directory pathref FD, reads the Gluster xattr with `fgetxattr()`, maps `ENOATTR` to `ENOENT`, and returns the xattr value as the found name.

State and persistence: the only module state is per-connection cached device mappings under the VFS handle. It does not persist data; it reads kernel mount state and Gluster xattrs to adapt Samba's runtime behavior.

Dependencies and integration points: depends on the host mount table (`setmntent()`/`getmntent()`), `stat()`, Linux xattr APIs, Samba file ID creation, and a lower VFS module/default filesystem implementation for ordinary operations. It is intentionally stackable and only overrides connect, file-id creation, and real-filename lookup.

Risks: `/etc/mtab` can be stale, hidden by containerization, or differ from `/proc/self/mounts`; cache reload only happens on misses. The hash is not collision-proof, so different Gluster fsnames can theoretically map to the same synthetic device. The real-name xattr path opens the directory and closes it manually; failures must preserve mapped NT status. Test signals include multiple Gluster FUSE mounts with different fsnames, mount table reload after remount, hash stability across process restarts, `ENOATTR` to not-found mapping, and file IDs remaining stable when the local FUSE device changes.
