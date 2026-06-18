<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.h -->
# Research: sources/user-network-fs/davfs2/src/cache.h

Purpose: public cache-layer interface and data model shared between the WebDAV cache implementation and kernel interface.

Important types: `dav_handle` tracks open local cache file descriptors with access flags and requester pid/pgid/uid. `dav_node` represents files/directories with parent/child/tree links, hash-table link, server path, display name, local cache path, ETag, open handles, size, atime/mtime/ctime/server mtime, update time, lock expiration, directory nlink count, remote-exists/dirty flags, mode, uid, and gid. `dav_node_list_item` supports changed/upload scheduling. `dav_stat` backs statfs output. `dav_write_dir_entry_fn` is the kernel-specific callback for serializing directory entries.

Control flow and integration: `dav_fuse.c` uses `dav_node *` as FUSE node IDs and calls these APIs for every filesystem request. `cache.c` owns all mutation. `dav_register_kernel_interface` lets the kernel layer provide directory-entry serialization and receive preferred block size.

State and persistence: declares structures that store both volatile in-memory state and references to persistent cache files. Fields such as `cache_path`, `etag`, `smtime`, `lock_expire`, `remote_exists`, and `dirty` are serialized by `cache.c` into the XML cache index.

Dependencies: requires POSIX types (`mode_t`, `uid_t`, `gid_t`, `pid_t`, `off_t`) and `dav_args` from `mount_davfs.h`.

Risks: public exposure of full `dav_node` internals couples kernel translation tightly to cache representation. Pointer-based inode identity makes stale pointers dangerous after node invalidation. Callers must respect documented permission and lifetime rules.

Test signals: compile-time ABI checks across source files, FUSE operations using node pointers through lookup/open/release, cache index round-trip preserving all required fields, and close/removal behavior for invalidated open nodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/cache.h -->
