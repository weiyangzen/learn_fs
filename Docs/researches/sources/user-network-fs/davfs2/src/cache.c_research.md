<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.c -->
# Research: sources/user-network-fs/davfs2/src/cache.c

Purpose: core davfs2 directory/file cache and FUSE upcall implementation target. It translates filesystem operations into WebDAV operations while maintaining an in-memory `dav_node` tree, on-disk cache files, dirty-file upload scheduling, lock refresh/release, local backup recovery, and a persistent XML cache index.

Important APIs: public functions implement the cache contract in `cache.h`: `dav_init_cache`, `dav_close_cache`, `dav_register_kernel_interface`, `dav_tidy_cache`, and upcalls `dav_access`, `dav_close`, `dav_create`, `dav_getattr`, `dav_lookup`, `dav_mkdir`, `dav_open`, `dav_read`, `dav_remove`, `dav_rename`, `dav_rmdir`, `dav_root`, `dav_setattr`, `dav_statfs`, `dav_sync`, `dav_write`.

Control flow: initialization sets globals from `dav_args`, creates the hash table and root, selects a per-mount cache directory, parses `index`, creates backup directory if missing, cleans orphaned cache files, then tries `PROPFIND` on root with retry tolerance. Kernel requests arrive through `dav_fuse.c`; each validates node existence/permissions, updates directories/files if refresh windows expired, invokes `webdav.c` helpers (`dav_get_collection`, `dav_get_file`, `dav_put`, `dav_lock`, `dav_unlock`, `dav_move`, `dav_delete`, `dav_quota`), and updates local node/cache state. `dav_tidy_cache` is called during idle loop to refresh locks, upload closed dirty files, release locks, resize cache, and optionally minimize memory.

State and persistence: global state includes `root`, `backup`, node hash `table`, `changed` queue, retry intervals, default uid/gid/modes, cache directory, cache size counters, and directory entry writer callback. Persistent state is the cache directory: file content cache, directory-list cache files, `lost+found` backups, and XML `index` written on close. Dirty or created files are retried with increasing delay and moved to backup/remove path after hard failures or too many attempts.

Important private helpers: `new_node`, `add_node`, `update_directory`, `update_node`, `update_cache_file`, `create_cache_file`, `create_dir_cache_file`, `write_dir`, `move_dir`, `move_reg`, `move_no_remote`, `remove_node`, `backup_node`, `clean_tree`, `resize_cache`, `parse_index`, `write_node`, and XML callbacks.

Dependencies/integration: depends on neon allocation/XML APIs, POSIX file APIs, user/group database, `defaults.h`, `mount_davfs.h` args, `webdav.h`, `util.h`, and the FUSE directory-entry callback registered by `dav_fuse.c`.

Risks: uses pointer values as inode/node IDs, so process-local validity and alignment/hash assumptions matter. The code is single-thread oriented; concurrent access would need external serialization. Upload failures and lock loss are data-integrity sensitive. XML index parsing deletes invalid trees, and cache backup behavior must be reliable. Some loops increment byte counters even after `write()` returns negative, which deserves review in adjacent FUSE writer code. Permission semantics are local-only and may diverge from remote server state.

Test signals: WebDAV integration tests for create/open/write/close/upload, delayed upload, lock refresh, remote conflict/lost update, rename over open files, cache eviction, XML index restart recovery, orphaned cache backup, user/group permission checks, quota/statfs, and unmount with dirty data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.c -->
