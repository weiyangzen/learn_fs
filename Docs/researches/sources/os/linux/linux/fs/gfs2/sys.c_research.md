# File Research: sources/os/linux/linux/fs/gfs2/sys.c

## Scope

This file implements GFS2 sysfs objects and attributes under the `gfs2` kset. It exposes mount identity/status, freeze and withdraw controls, quota/statfs sync triggers, glock demotion, lock-module controls, journal recovery controls, journal id/first-mounter assignment, and tunables.

## Public And Internal APIs Covered

- Generic sysfs plumbing: `struct gfs2_attr`, `gfs2_attr_show()`, `gfs2_attr_store()`, `gfs2_ktype`, `gfs2_uevent_ops`.
- Filesystem attributes: `id`, `fsname`, `uuid`, `freeze`, `withdraw`, `statfs_sync`, `quota_sync`, `quota_refresh_user`, `quota_refresh_group`, `demote_rq`, `status`.
- Lock module attributes: `proto_name`, `block`, `withdraw`, `jid`, `first`, `first_done`, `recover`, `recover_done`, `recover_status`.
- Tunables: quota warning/quantum/scale, max readahead, complaint period, statfs slow/quantum, new-files jdata, withdraw helper timeout.
- Exported functions: `gfs2_sys_fs_add()`, `gfs2_sys_fs_del()`, `gfs2_sys_init()`, `gfs2_sys_uninit()`, `gfs2_recover_set()`.

## Control Flow And Behavior

`gfs2_sys_fs_add()` initializes the per-mount kobject with the table name, creates the default, `tune`, and `lock_module` groups, links the block device as `device`, and emits a `KOBJ_ADD` uevent with read-only and spectator state. Teardown removes the link/groups, puts the kobject, and waits for `sd_kobj_unregister`.

Identity and status attributes expose device number, filesystem name, UUID, and detailed `sd_flags`/log counters. `freeze_store()` accepts only `0` or `1` from CAP_SYS_ADMIN and invokes VFS thaw/freeze. `withdraw_store()` accepts only `1`, logs a user-requested cluster withdraw, and calls `gfs2_withdraw()`.

Quota/statfs controls require CAP_SYS_ADMIN and accept `1` as a trigger. User and group quota refresh parse ids into `kqid` values in the current user namespace and call `gfs2_quota_refresh()`.

`demote_rq_store()` parses `<gltype>:<glnum> <mode>`, maps textual modes to GFS2 lock states, resolves the right glock operations including the special freeze glock, sets `SDF_DEMOTE` once, gets the glock without creation, issues a callback demotion, and puts the glock.

Lock-module controls expose protocol name and DLM-style block/unblock. Clearing block mode uses a memory barrier and thaws glocks. The helper withdraw status attribute completes `sd_withdraw_helper` with status 0 or 1 for the offline uevent flow in `util.c`.

Journal id and first-mounter stores wait for locking initialization, take `sd_jindex_spin`, and only allow changes while `SDF_NOJOURNALID` is still set. Spectator mounts cannot claim a positive journal id. `gfs2_recover_set()` waits for the local journal to be ready, rejects recovery of the local journal on non-spectator mounts, finds the requested journal descriptor, and queues recovery.

Tunables are read and updated under `gt_spin`; setters require CAP_SYS_ADMIN and optionally reject zero.

## State And Data Structures

The file manipulates `sd_kobj`, `sd_kobj_unregister`, `sd_flags`, `sd_lockstruct`, `sd_jdesc`, log counters, tunables in `sd_tune`, `sd_withdraw_helper_status`, `sd_withdraw_helper`, `sd_locking_init`, and the global `gfs2_kset`.

## Dependencies

It depends on Linux kobject/sysfs/kset APIs, capability checks, current user namespace quota ids, block-device kobjects, and GFS2 glock, quota, statfs, recovery, freeze, and withdraw subsystems.

## Risks And Invariants

Most store handlers are privileged because they can freeze the filesystem, withdraw the mount, alter quota state, trigger recovery, or force glock demotion. Journal id and first-mount assignment are valid only before mount locking has completed journal selection. Sysfs teardown must wait for kobject release before freeing the superblock. `demote_rq` accepts raw glock identifiers, so strict parsing and glock type validation are important.
