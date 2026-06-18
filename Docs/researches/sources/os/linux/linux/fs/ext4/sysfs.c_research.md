# File Research: sources/os/linux/linux/fs/ext4/sysfs.c

## Purpose
Implements ext4’s sysfs and procfs surface for per-mounted-filesystem tunables/statistics, supported feature advertisement, and error notification.

## Main Elements
- Attribute model: `struct ext4_attr`, `attr_id_t`, `attr_ptr_t`, macros for explicit, `ext4_sb_info`, and on-disk superblock-backed attributes.
- Read-only counters/status: delayed allocation blocks, session/lifetime write kbytes, exceeded retry count, warning/message/error counters, first/last error metadata, journal task pid.
- Writable tunables: reserved clusters, inode readahead blocks, mballoc scan/prealloc parameters, extent zeroout limit, ratelimit settings, prefetch settings, trim threshold, superblock update interval/size, and error report interval.
- Test/debug hooks: `trigger_fs_error` requires `CAP_SYS_ADMIN`; `simulate_fail` exists under `CONFIG_EXT4_DEBUG`.
- Feature directory: advertises supported features such as lazy inode-table init, batched discard, meta_bg resize, encryption, casefold, verity, metadata checksum seed, fast commit, encrypted casefold, and blocksize greater than page size when configured.
- Procfs registration: creates `/proc/fs/ext4/<dev>/options`, `es_shrinker_info`, `fc_info`, `mb_groups`, `mb_stats`, and `mb_structs_summary`.
- Lifecycle: `ext4_init_sysfs()`, `ext4_exit_sysfs()`, `ext4_register_sysfs()`, `ext4_unregister_sysfs()`, and `ext4_notify_error_sysfs()`.

## Dependencies And Integration
Hooks into kobject/sysfs, procfs, block statistics, ext4 mballoc and fast-commit seq interfaces, and error-reporting state maintained in `super.c`. Per-superblock registration occurs late in mount after core initialization and is unregistered early during unmount.

## Behavioral Notes
Generic show/store paths compute pointers from either `ext4_sb_info`, `ext4_super_block`, or explicit storage. Stores validate bounds for power-of-two readahead, reserved-cluster count, mballoc order/group limits, and error-report intervals. Error sysfs notification is serialized with `s_error_notify_mutex` to avoid races with kobject deletion.

## Risk Notes
Writable sysfs attributes directly mutate live allocator and reporting tunables, so validation is the main safety boundary. Attributes backed by on-disk superblock fields must handle endianness correctly. Registration order matters because proc/sysfs readers can race with unmount and journal teardown.
