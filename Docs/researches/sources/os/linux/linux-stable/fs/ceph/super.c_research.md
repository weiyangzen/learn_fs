# File Research: sources/os/linux/linux-stable/fs/ceph/super.c

## Purpose
Implements CephFS filesystem registration, mount option parsing, fs-context operations, superblock setup/sharing, root open, unmount/shutdown/reconnect handling, cache initialization, and module parameters.

## Main Interfaces
- Super operations: `ceph_put_super()`, `ceph_statfs()`, `ceph_sync_fs()`, `ceph_umount_begin()`, `ceph_super_ops`.
- Mount parsing: `ceph_parse_mount_param()`, `ceph_parse_source()`, `ceph_parse_mon_addr()`.
- Client lifecycle: `create_fs_client()`, `destroy_fs_client()`.
- Mount lifecycle: `ceph_init_fs_context()`, `ceph_get_tree()`, `ceph_real_mount()`, `ceph_kill_sb()`.
- Recovery/module: `ceph_force_reconnect()`, `init_ceph()`, `exit_ceph()`.

## Control Flow
Mount setup starts with `ceph_init_fs_context()`, which allocates generic Ceph options and CephFS mount options with defaults. `ceph_parse_mount_param()` accepts both libceph parameters and CephFS-specific options such as sizes, readdir limits, snapdir name, namespace, fscache, ACLs, pagecache bypass, sparse read, async dir ops, and dummy encryption.

`ceph_get_tree()` validates source syntax, creates a new `ceph_fs_client`, initializes the MDS client, and uses `sget_fc()` to either share an existing superblock with matching options or install a new one via `ceph_set_super()`. `ceph_real_mount()` opens the cluster session, registers fscache/debugfs as needed, applies dummy encryption, sends a root `GETATTR` request, and installs the root dentry.

Unmount begins with MDS pre-umount and workqueue flush, then forces `sync_filesystem()`, waits for dirty folios and stopping blockers, kills the anonymous superblock, cleans debugfs/fscache, and destroys the fs client. Forced reconnect aborts OSD/MDS requests, invalidates open file generations, resets client address/abort state, and refreshes root attributes.

## State And Synchronization
Global `ceph_fsc_list` is protected by `ceph_fsc_lock` and is used for metrics wakeups when the module parameter changes. Mount operations serialize on `client->mount_mutex`. Stopping blockers use `mdsc->stopping_lock`, `stopping_blockers`, and `stopping_waiter` to prevent teardown while metadata or data I/O is active.

## Integration Points
Connects VFS fs-context and superblock APIs to libceph client creation, monitor map dispatch, MDS map/fsmap handling, MDS request execution, fscache, fscrypt, debugfs, quota statfs, and CephFS inode/dentry/export/xattr operations.

## Risks And Review Focus
- Source parsing supports old and new mount syntaxes; namespace and monitor-address validation must remain exact.
- Superblock sharing depends on complete option comparison and blocklist/shutdown state checks.
- Unmount ordering is sensitive: accepting late MDS messages after flush can resurrect inode refs.
- Reconfigure only updates a limited option subset; new remount-mutability should be deliberate.
