# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/handle.c

Purpose: Implements LizardFS object-handle operations for namespace manipulation, metadata, file open/reopen/close, read/write/commit, share reservation, locking, wire handles, and object op registration.

Important APIs and types: Registered methods include `release`, `merge`, `lookup`, `mkdir`, `mknode`, `readdir`, `symlink`, `readlink`, `getattrs`, `link`, `rename`, `unlink`, `close`, `handle_to_wire`, `handle_to_key`, `open2`, `status2`, `reopen2`, `read2`, `write2`, `commit2`, `setattr2`, `close2`, `lock_op2`, `close_func`, and `reopen_func`. Private helpers include `lzfs_int_close_fd`, `lzfs_reopen_func`, `lzfs_int_open_by_handle`, `lzfs_int_open_by_name`, and `lzfs_int_close_func`.

Control flow: Namespace operations translate FSAL calls into `liz_cred_*` operations and allocate handles from returned `struct stat`. Open paths either reopen an existing inode, look up an existing child, or create a file via `liz_cred_mknod()`, optionally apply attributes, then open by handle. I/O uses Ganesha `fsal_start_io()`/`fsal_complete_io()` to select state/global/temp fds and enforce share rules, then loops over iovecs with `liz_cred_read()` or `liz_cred_write()`. Metadata updates build LizardFS setattr masks and optionally ACL updates. Locks translate FSAL locks to `liz_lock_info_t` and call LizardFS getlk/setlk.

State and persistence: Handles store inode, unique key, export pointer, share counters, and a global `lzfs_fsal_fd`. Per-state fds come from export state allocation. Persistent state is delegated to LizardFS; handle state controls Ganesha caching and open/share behavior.

Dependencies and integration: Depends on FSAL fd/share helpers, `context_wrap`, `lzfs_internal`, LizardFS error codes, ACL helpers, and optional pNFS MDS ops. It is initialized from `lzfs_fsal_new_handle()`.

Risks: `lzfs_int_open_by_handle()` calls `lzfs_reopen_func(obj_hdl, openflags | after_mknod ? 0x1000 : 0, ...)`; C precedence makes this effectively `(openflags | after_mknod) ? 0x1000 : 0`, likely losing requested open flags. `write2()` assigns then adds `nb_written`, double-counting each iovec. `read2()` has a suspicious `offset == 0` EOF check where `nb_read == 0` was likely intended. `close2()` updates share counters using the global fd's openflags instead of the state fd's openflags. Several create paths return success after failed post-create `setattr2()` while clearing `new_obj`.

Test signals: Open/reopen with every NFS open flag combination, exclusive create verifier, truncate, read/write multi-iovec byte counts, stateless I/O share release, close2 share counters, lock leak/regression tests, mknode rawdev creation, ACL get/set through getattr/setattr, and pNFS-enabled layout ops installation.
