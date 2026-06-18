# File Research: sources/os/linux/linux/fs/autofs/expire.c

## Summary
Implements autofs expiration selection and synchronization for direct, indirect, tree, leaf, and forced expiration modes.

## Main Responsibilities
- Determine whether dentries are old enough and idle enough to expire.
- Check mount trees for busyness using dentry refcounts and `may_umount_tree()`.
- Traverse positive dentries safely under autofs lookup locking.
- Mark dentries as `WANT_EXPIRE` and `EXPIRING`.
- Coordinate with wait queues and daemon expiry notifications.
- Provide root ioctl and misc-device expire entry points.

## Key APIs
- `autofs_expire_wait()`.
- `autofs_expire_run()`.
- `autofs_do_expire_multi()`.
- `autofs_expire_multi()`.

## Important Behavior
Expiration eligibility uses `last_used + timeout` unless `AUTOFS_EXP_IMMEDIATE` is requested. Forced expiration bypasses normal busy checks and lets userspace handle busy mounts.

Direct mount expiration checks the root dentry and mount tree. Indirect expiration scans positive root children, supports per-dentry timeouts, and can expire either whole trees or leaves depending on flags.

Before final selection, dentries are marked `AUTOFS_INF_WANT_EXPIRE` and an RCU grace period is forced with `synchronize_rcu()`. The code then revalidates that the dentry is still eligible before setting `AUTOFS_INF_EXPIRING`.

`autofs_expire_wait()` blocks path walkers while an expire is pending or active, using `autofs_wait()` and `expire_complete`.

## Risks
Expiration is race-prone by design: path walking, daemon unlink/rmdir, mountpoint replacement, RCU walk, dentry refcounts, and umount checks all interact. The `WANT_EXPIRE` to `EXPIRING` transition and cleanup must clear flags and complete waiters on every path.
