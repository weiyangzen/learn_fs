# File Research: sources/os/linux/linux/fs/afs/write.c

## Scope

This file integrates AFS regular-file writeback with netfs: selecting writeback keys, issuing store-data RPCs, retrying with alternate keys, fsync validation, page-mkwrite validation, and pruning writeback key records.

## Public And Internal APIs Covered

- Netfs hooks: `afs_prepare_write()`, `afs_issue_write()`, `afs_begin_writeback()`, `afs_retry_request()`.
- VFS hooks: `afs_writepages()`, `afs_fsync()`, `afs_page_mkwrite()`.
- Key cleanup: `afs_prune_wb_keys()`.

## Control Flow And Behavior

- Writeback key selection walks `vnode->wb_keys` starting after the previous key, chooses the first valid key, and stores both the key and key record in the netfs request.
- Store-data completion commits returned status, records ctime, prunes keys, and updates store counters/byte stats.
- `afs_prepare_write()` sets a large stream subrequest maximum length.
- `afs_issue_write_worker()` allocates an uninterruptible AFS operation, sets vnode modification/data-version delta, position, length, write iterator, target size, and mtime, then waits for operation completion and reports progress to netfs.
- Permission/key errors mark the subrequest for retry if another writeback key is available.
- `afs_retry_request()` rotates writeback keys for write origins on credential failures and marks the stream failed if no valid key remains.
- `afs_writepages()` takes `validate_lock` to avoid racing with truncate/setattr page-cache invalidation.
- `afs_fsync()` validates the vnode with the file key before waiting on dirty pages.
- `afs_page_mkwrite()` validates before allowing netfs to make a page writable.

## State And Data Structures

- `vnode->wb_keys` stores authorizing keys used for dirty data.
- Netfs request private fields carry the selected `struct key` and `struct afs_wb_key`.

## Dependencies

- Netfs writeback APIs, AFS operation framework, StoreData RPC implementations, key validation, inode/page-cache writeback, and validation code.

## Risks And Invariants

- Writes must use credentials that authorized the dirtying process when possible.
- Validation lock prevents writeback racing with cache truncation.
- Key records are pruned only when no dirty/writeback tags remain and their usage count is otherwise idle.
