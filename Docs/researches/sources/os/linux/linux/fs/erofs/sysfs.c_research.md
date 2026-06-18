# File Research: sources/os/linux/linux/fs/erofs/sysfs.c

## Purpose
Provides EROFS sysfs objects and attributes for global feature reporting and per-mounted-superblock tuning/debug controls.

## Main Elements
- Attribute descriptors: `struct erofs_attr` plus macros for feature, integer, boolean, and function-backed sysfs attributes.
- Per-superblock attributes: `sync_decompress`, `drop_caches`, and `dir_ra_bytes`, gated by compression configuration where relevant.
- Global attributes: optional compression acceleration engine control and the `features` kobject entries for supported on-disk features such as compression configs, big pclusters, chunked files, device tables, superblock checksums, fragments, dedupe, 48-bit layout, and metabox.
- Generic show/store dispatch: `erofs_attr_show()` and `erofs_attr_store()` map attributes to offsets in `struct erofs_sb_info` or `struct erofs_mount_opts`, parse user input, validate values, drop compressed-data caches, invalidate managed pages, and enable/disable crypto acceleration engines.
- Object lifecycle: `erofs_register_sysfs()`, `erofs_unregister_sysfs()`, `erofs_init_sysfs()`, and `erofs_exit_sysfs()` manage the `/sys/fs/erofs` kset, the global `features` kobject, and per-superblock kobjects.

## Dependencies And Integration
Used by `super.c` during mount and unmount. It integrates with Linux kobjects/sysfs, the EROFS compression cache shrinker, managed cache mapping invalidation, and optional accelerated decompression crypto engine controls.

## Risk Notes
The pointer-offset attribute mechanism is compact but depends on correct `struct_type` and `offset` metadata. Store handlers directly mutate mounted filesystem runtime fields, so validation is limited to each attribute's known range. Sysfs unregister waits for kobject completion to avoid freeing `erofs_sb_info` while sysfs references still exist.
