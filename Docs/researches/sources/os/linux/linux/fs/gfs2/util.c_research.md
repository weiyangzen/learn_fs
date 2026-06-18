# File Research: sources/os/linux/linux/fs/gfs2/util.c

## Scope

This file implements global cache pointers, assertion/consistency/error reporting, spectator journal-clean checks, freeze glock helpers, and filesystem withdrawal behavior.

## Public And Internal APIs Covered

- Cache globals: `gfs2_glock_cachep`, `gfs2_glock_aspace_cachep`, `gfs2_inode_cachep`, `gfs2_bufdata_cachep`, `gfs2_rgrpd_cachep`, `gfs2_quotad_cachep`, `gfs2_qadata_cachep`, `gfs2_trans_cachep`, `gfs2_page_pool`.
- Clean/freeze helpers: `check_journal_clean()`, `gfs2_freeze_lock_shared()`, `gfs2_freeze_unlock()`.
- Withdrawal: `gfs2_withdraw()`, `gfs2_withdraw_func()`, internal `do_withdraw()`, `gfs2_offline_uevent()`.
- Diagnostics: `gfs2_lm()`, `gfs2_assert_i()`, `gfs2_assert_withdraw_i()`, `gfs2_assert_warn_i()`, `gfs2_consist_i()`, `gfs2_consist_inode_i()`, `gfs2_consist_rgrpd_i()`, metadata/type check reporters, and I/O error reporters.

## Control Flow And Behavior

`check_journal_clean()` locks a journal inode glock shared with recovery/exact/nocache flags, validates journal size/allocation, reads the journal head, and returns `-EPERM` if the journal lacks the clean unmount flag. This protects spectator mounts from becoming first mounters of dirty journals.

`gfs2_freeze_lock_shared()` and `gfs2_freeze_unlock()` manage the shared freeze glock holder used by mount/thaw paths. Errors other than try-failed are logged.

`gfs2_withdraw()` honors the configured error policy. In withdraw/deactivate modes it atomically sets `SDF_WITHDRAWN`, dumps a stack, skips work if the superblock is not born yet, logs the pending withdrawal, and schedules `sd_withdraw_work`. Panic mode panics immediately.

`gfs2_withdraw_func()` refuses to run during kill/unmount and asserts debug mode is off. It sends a `KOBJ_OFFLINE` uevent through `gfs2_offline_uevent()` so userspace can deactivate the shared block device. Depending on whether the device became inactive and whether the lock module provides `lm_unmount`, it orders lock-module unmount and `do_withdraw()` to either permit immediate remote recovery or drain local state first. Deactivate mode panics if the helper fails to deactivate the device.

`do_withdraw()` takes the log flush write lock, clears `SDF_JOURNAL_LIVE`, drains AIL transactions, wakes log/quota waiters, waits briefly for an empty log, marks the VFS superblock read-only, and dequeues pending non-system glock holders that cannot be granted after withdrawal.

Consistency helpers log fsid-qualified fatal messages and call `gfs2_withdraw()`. Inode and rgrp consistency paths also dump the relevant glock/rgrp state. Warning assertions are rate-limited by `gt_complain_secs`, can BUG in debug mode, and panic in panic error mode.

## State And Dependencies

The file manipulates `sd_flags`, `sd_log_flush_lock`, log wait queues, quota wait queues, `sd_kobj`, withdraw helper completion/status, lock module operations, freeze holder state, and tunables. It depends on GFS2 log, recovery, glock, rgrp, super, and sysfs subsystems.

## Risks And Invariants

Withdrawal must stop journal liveness before draining transactions and must prevent new write transactions. Shared block-device deactivation ordering affects cluster safety: if the device is inactive, remote recovery can begin sooner; otherwise local caches must drain before lock-module unmount. Consistency reporters must avoid duplicate noisy logging once already withdrawn. Freeze glock holder state must be initialized/uninitialized exactly once.
