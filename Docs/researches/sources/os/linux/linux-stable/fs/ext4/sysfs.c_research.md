# File Research: sources/os/linux/linux-stable/fs/ext4/sysfs.c

## Purpose

`sysfs.c` implements ext4's global and per-mounted-filesystem sysfs/procfs interface. It creates `/sys/fs/ext4`, `/sys/fs/ext4/features`, per-superblock sysfs attribute groups, and `/proc/fs/ext4/<dev>/` diagnostic files.

## Attribute Model

The file defines a compact attribute descriptor:

- `struct ext4_attr` wraps `struct attribute`.
- `attr_id_t` identifies custom show/store behavior or primitive pointer formatting.
- `attr_ptr_t` says whether the attribute points to an explicit global, an offset in `struct ext4_sb_info`, or an offset in `struct ext4_super_block`.
- Macros such as `EXT4_ATTR_FUNC`, `EXT4_ATTR_OFFSET`, `EXT4_RO_ATTR_ES_UI`, `EXT4_RW_ATTR_SBI_UI`, and `EXT4_ATTR_FEATURE` declare most attributes.

Pointer-backed attributes are resolved by `calc_ptr()` and displayed or updated by generic show/store helpers.

## Per-Mount Sysfs Attributes

The per-superblock `ext4_attrs` group exposes operational counters and tunables, including:

- Delayed allocation blocks.
- Session and lifetime write kilobytes.
- Reserved clusters.
- SRA retry-limit counter.
- Inode readahead blocks.
- Mballoc tunables such as `mb_stats`, scan limits, stream/group preallocation, prefetch, prefetch limit, and trim settings.
- Extent zeroout limit.
- Error injection through `trigger_fs_error`.
- Error, warning, and normal-message ratelimit interval/burst tunables.
- Error counters and first/last error metadata from the on-disk superblock.
- Journal task pid.
- Superblock update cadence through `sb_update_sec` and `sb_update_kb`.
- Daily error-reporting interval through `err_report_sec`.
- Debug-only `simulate_fail` when `CONFIG_EXT4_DEBUG` is enabled.

## Feature Sysfs Attributes

The global `/sys/fs/ext4/features` group reports supported ext4 features as `"supported\n"`:

- `lazy_itable_init`
- `batched_discard`
- `meta_bg_resize`
- `metadata_csum_seed`
- `fast_commit`
- Optional encryption, dummy encryption v2, casefold, verity, encrypted casefold, and blocksize greater than page size depending on kernel config.

## Show/Store Behavior

Important helpers:

- `session_write_kbytes_show()` reports sectors written since mount.
- `lifetime_write_kbytes_show()` combines persisted lifetime write kbytes with current-session device writes.
- `inode_readahead_blks_store()` accepts zero or a power of two up to `0x40000000`.
- `reserved_clusters_store()` validates the value is less than total clusters and stores it in `s_resv_clusters`.
- `trigger_test_error()` requires `CAP_SYS_ADMIN` and injects an ext4 error using the written string.
- `err_report_sec_store()` validates interval up to one year, starts/stops/reprograms the error-report timer, and returns the write count.
- `journal_task_show()` reports `<none>` without a journal or the JBD2 task pid otherwise.
- `ext4_generic_attr_show()` formats integer, string, atomic, little-endian superblock, and pointer-backed values.
- `ext4_generic_attr_store()` parses and validates writable pointer-backed integer attributes.
- `ext4_attr_show()` dispatches special attributes and feature attributes.
- `ext4_attr_store()` dispatches special stores and falls back to generic stores.

## Kobject and Proc Lifecycle

- `ext4_init_sysfs()` creates the global `ext4_root` kobject under `fs_kobj`, allocates and registers the `features` kobject, and creates the `/proc/fs/ext4` root.
- `ext4_register_sysfs()` initializes the per-superblock kobject under `/sys/fs/ext4/<sb-id>` and creates proc entries under `/proc/fs/ext4/<sb-id>/`.
- Per-mount proc entries include:
  - `options`
  - `es_shrinker_info`
  - `fc_info`
  - `mb_groups`
  - `mb_stats`
  - `mb_structs_summary`
- `ext4_unregister_sysfs()` removes the proc subtree and deletes the per-superblock kobject.
- `ext4_exit_sysfs()` drops global kobjects and removes `/proc/fs/ext4`.
- `ext4_sb_release()` completes `s_kobj_unregister`, which unmount waits on before freeing `ext4_sb_info`.
- `ext4_feat_release()` frees the dynamically allocated feature kobject.
- `ext4_notify_error_sysfs()` notifies the `errors_count` sysfs file when new errors are committed, protected by `s_error_notify_mutex`.

## Integration Points

This file is called from `super.c` during ext4 module init/exit, mount completion, unmount, and deferred superblock error update work. It depends on mballoc, fast commit, extent-status shrinker, and option display functions to populate proc diagnostics.

## Edge Cases

- Per-superblock kobject registration is synchronized with error notifications through `s_error_notify_mutex`.
- On registration failure, the code calls `kobject_put()` and waits for completion before returning.
- `journal_task_show()` tolerates filesystems without a journal.
- `err_report_sec_store()` handles enable, disable, and interval update paths without leaving stale timers active.
- Attribute stores validate ranges for tunables that feed allocator or timer behavior.
