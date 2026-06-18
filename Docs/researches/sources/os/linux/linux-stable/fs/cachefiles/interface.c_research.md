# File Research: sources/os/linux/linux-stable/fs/cachefiles/interface.c

This file implements the FS-Cache-facing CacheFiles backend operations for cookie/object lifecycle, resize, invalidation, lookup, withdrawal, and operation setup.

Primary object lifecycle:
- `cachefiles_alloc_object()` allocates a `struct cachefiles_object`, initializes locking/refcount/list fields, links it to the volume and cookie, assigns a debug id, and initializes on-demand metadata if needed.
- `cachefiles_grab_object()`, `cachefiles_see_object()`, and `cachefiles_put_object()` provide traced object reference management. Final release requires no open file, frees the cooked name, on-demand info, cookie reference, and slab object.
- `cachefiles_lookup_cookie()` creates the object, cooks the object key into a filename, looks up or creates backing storage, links it to the active object list, and adjusts backing file size.
- `cachefiles_withdraw_cookie()` removes an active object from the cache list, cleans on-demand state, commits or deletes the backing file, closes it, clears `cookie->cache_priv`, and drops the object reference.
- `cachefiles_invalidate_cookie()` replaces the current backing file with an unlinked tmpfile, marks content empty and needing update, resumes FS-Cache invalidation, and buries the old object if necessary.

Size and coherency handling:
- `cachefiles_adjust_size()` rounds object size to `CACHEFILES_DIO_BLOCK_SIZE`, truncates/discards partial tail pages when extending, and sets the backing file size.
- `cachefiles_shorten_object()` truncates a file to rounded DIO size and zero-fills the tail range when the logical object size is not DIO-aligned.
- `cachefiles_resize_cookie()` shrinks backing storage when needed and updates cookie object size.
- `cachefiles_commit_object()` writes xattrs when local writes or updates occurred and links tmpfiles into place.

FS-Cache ops exported:
- `cachefiles_cache_ops` supplies `acquire_volume`, `free_volume`, `lookup_cookie`, `withdraw_cookie`, `invalidate_cookie`, `begin_operation`, `resize_cookie`, and `prepare_to_write`.

Important behavior:
- Tmpfiles are used for invalidation and new object creation, then committed atomically by link in `namei.c`.
- Retired cookies delete existing non-tmpfile objects.
- Local-write and update flags drive xattr coherency updates.
- Object file pointer substitution is protected by `object->lock`.
