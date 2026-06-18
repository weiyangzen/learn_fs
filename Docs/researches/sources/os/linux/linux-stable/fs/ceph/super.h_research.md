# File Research: sources/os/linux/linux-stable/fs/ceph/super.h

## Purpose
Defines the central CephFS kernel-client data structures, mount option flags, inode/cap/snapshot/xattr state, helper inlines, and cross-file prototypes.

## Main Contents
- Mount definitions: block sizing, default read/write/readdir/readahead limits, snapdir name, mount option flags, and `struct ceph_mount_options`.
- Client state: `struct ceph_fs_client` with superblock, mount options, libceph client, MDS client, mount state, workqueues, fscache/debugfs/fscrypt state, async unlink tracking, and writeback congestion.
- Capability state: `struct ceph_cap`, `struct ceph_cap_flush`, `struct ceph_cap_snap`, cap reference helpers, dirty/flushing state, and prototypes for caps code.
- Inode state: `struct ceph_inode_info` embedding `netfs_inode`, Ceph vino, layout, directory stats, quotas, subvolume ID, fragtree, xattrs, caps, cap snaps, snap realm/map union, truncation/writeback fields, fscrypt data, work bits, and flags.
- Dentry/file state: `struct ceph_dentry_info`, `struct ceph_file_info`, `struct ceph_dir_file_info`, `struct ceph_rw_context`, and readdir cache control.
- Snapshot state: `struct ceph_snap_realm` and snap-related prototypes.
- Prototypes for inode, xattr, ACL, file, dir, ioctl, export, lock, quota, debugfs, and stopping-blocker functions.

## Important Helpers
The header provides conversion helpers between VFS objects and CephFS objects, inode number presentation with `ino32`, reserved inode filtering, directory completeness sequence helpers, quota update helpers, capability-issued wrappers, workqueue scheduling helpers, and `ceph_inode_is_shutdown()`.

## Integration Points
Almost every CephFS implementation file includes this header. It is the shared contract between superblock/mount code, inode metadata, caps, MDS client, xattr, directory, file I/O, quota, fscrypt, fscache, and netfs paths.

## Risks And Review Focus
- Structure fields encode lock ownership assumptions; changing them without matching lock rules can break caps, xattrs, or snapshot flushing.
- `ceph_inode_info` has many cross-subsystem fields, making initialization and eviction consistency important.
- Inline helpers such as directory completeness and mount-state shutdown checks are used on fast paths and must preserve memory-ordering assumptions.
