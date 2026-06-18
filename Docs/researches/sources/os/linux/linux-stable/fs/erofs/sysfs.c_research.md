# File Research: sources/os/linux/linux-stable/fs/erofs/sysfs.c

This file implements EROFS sysfs registration and runtime attributes under `/sys/fs/erofs`.

Major responsibilities:
- Defines the root EROFS kset, the global `features` kobject, and per-superblock kobjects.
- Publishes supported feature attributes: `compr_cfgs`, `big_pcluster`, `chunked_file`, `device_table`, `compr_head2`, `sb_chksum`, `ztailpacking`, `fragments`, `dedupe`, `48bit`, and `metabox`.
- Publishes per-superblock tunables including `dir_ra_bytes`, and when compression is enabled, `sync_decompress` and `drop_caches`.
- Publishes compression-accelerator configuration through `accel` when `CONFIG_EROFS_FS_ZIP_ACCEL` is enabled.
- Implements generic attribute show/store dispatch through `struct erofs_attr`, struct-offset metadata, and attr ids.
- Registers per-superblock sysfs directories with `erofs_register_sysfs()` and removes them with `erofs_unregister_sysfs()`.
- Initializes and exits global sysfs state through `erofs_init_sysfs()` and `erofs_exit_sysfs()`.

Runtime behavior:
- Feature attributes read as `supported`.
- Unsigned integer and boolean attributes are read/written directly through validated struct offsets.
- `sync_decompress` writes are range-checked against EROFS sync-decompression modes.
- `drop_caches` accepts values 1 through 3 and can invalidate managed compressed-cache pages and/or shrink cached pclusters.
- `accel` writes disable all crypto acceleration engines, then enables newline-separated engine names from the input buffer.

Lifetime model:
- Per-superblock kobject release completes `s_kobj_unregister`, and unregister waits for that completion.
- Failed per-superblock kobject creation calls `kobject_put()` and waits for release, avoiding leaking partially initialized sysfs objects.
- Global init registers the `erofs` kset under `fs_kobj`, then adds the `features` kobject; failure unwinds through `erofs_exit_sysfs()`.
