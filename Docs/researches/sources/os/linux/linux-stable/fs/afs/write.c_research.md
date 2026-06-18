# File Research: sources/os/linux/linux-stable/fs/afs/write.c

## Scope

Integrates AFS regular-file writeback with the netfs library and fileserver StoreData RPCs.

## APIs And Behavior

- `afs_begin_writeback()` selects a valid cached author key for regular-file writeback.
- `afs_prepare_write()` sets the stream subrequest max length.
- `afs_issue_write()` queues `afs_issue_write_worker()`, which builds a StoreData operation, sets vnode modification/data-version delta, attaches the subrequest iterator, waits for completion, and terminates the netfs subrequest.
- `afs_retry_request()` rotates writeback keys after auth/key failures.
- `afs_writepages()` wraps `netfs_writepages()` under `validate_lock` to avoid races with truncation/status validation.
- `afs_fsync()` validates the vnode with the file key and then waits on dirty/writeback pages.
- `afs_page_mkwrite()` validates before allowing writable mmap faults.
- `afs_prune_wb_keys()` drops unused writeback keys once no dirty/writeback pages remain.

## State And Dependencies

Uses vnode writeback key lists, netfs writeback requests/subrequests, `afs_operation`, StoreData AFS/YFS RPCs, vnode status commit, page-cache tags, and validation locks.

## Risks And Invariants

Writes may need to retry with different author keys. StoreData operations are marked uninterruptible and advance data version by one. Writeback avoids blocking async callers on `validate_lock` in `WB_SYNC_NONE`.
