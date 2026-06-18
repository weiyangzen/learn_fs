# File Research: sources/os/linux/linux/fs/ceph/super.h

Primary internal CephFS header. It defines mount options, filesystem client state, inode-private state, capability structures, snap realm structures, inline helpers, and cross-file function declarations.

Key definitions:
- Mount option bits including clean recovery, dirstat/rbytes, async readdir, dcache, ino32, fscache, pool permissions, quota statfs behavior, copy-from, async dirops, nopagecache, and sparse read.
- Defaults for block/statfs size, read/write size, readahead, readdir limits, snapdir name, and cap-wanted delays.
- `struct ceph_mount_options`: parsed CephFS mount settings and string options.
- `struct ceph_fs_client`: superblock link, mount options, libceph client, MDS client, workqueues, writeback/congestion state, async unlink conflict table, debugfs dentries, fscache volume, fscrypt dummy policy.
- Capability types: `struct ceph_cap`, `struct ceph_cap_flush`, `struct ceph_cap_snap`.
- Inode support types: directory fragments, xattrs, dentry info, xattr cache info, netfs request data.
- `struct ceph_inode_info`: the central inode-private object containing vino, layout, dir stats, quota state, subvolume ID, frag tree, xattrs, caps, dirty/flushing lists, snap state, truncate/max-size state, cap refs, unsafe ops, work item, and optional fscrypt state.
- Readdir/file private state: `ceph_file_info`, `ceph_dir_file_info`, `ceph_rw_context`, `ceph_readdir_cache_control`.
- `struct ceph_snap_realm`: snapshot realm topology and cached context.

Inline helpers:
- Type conversion/accessors: `ceph_inode()`, `ceph_sb_to_fs_client()`, `ceph_inode_to_client()`, `ceph_vino()`, `ceph_ino()`, `ceph_snap()`.
- User-visible inode number conversion with `ino32`.
- Reserved inode filtering for MDS-private ranges.
- Directory completeness/order counters with memory barriers.
- Capability query wrappers and dirty-cap helper.
- RW context add/remove/find helpers.
- Default congestion calculation based on RAM, capped at 256 MiB.
- Pending cap-snap test.
- Inode shutdown test using inode flag or mount state.
- Quota state checks and update helper.
- Sparse-read extent-count helper for encrypted files.

Declared subsystem API surface:
- Super/mount: `ceph_force_reconnect()`, `ceph_umount_begin()`.
- Snap: realm lookup/refcount/update/handle, cap-snap finish, snapid map lifecycle.
- Inode/trace/readdir/fill/attrs.
- Xattr and security context helpers.
- ACL helpers, with stubs when ACL disabled.
- Capability management.
- File, dir, ioctl, export, lock, debugfs, and quota APIs.
- Stopping blocker APIs for MDS and OSD request paths.

Notable local addition:
- `CEPH_SUBVOLUME_ID_NONE` and `i_subvolume_id` are defined in `ceph_inode_info` for per-subvolume metrics; unknown/unset is represented as 0.
