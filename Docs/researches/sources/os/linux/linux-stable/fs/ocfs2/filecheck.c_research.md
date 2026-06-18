# File Research: sources/os/linux/linux-stable/fs/ocfs2/filecheck.c

Purpose: Implements OCFS2 online file check sysfs support, allowing administrators to queue inode check/fix requests and inspect recent results.

Read coverage: complete file read, 509 lines.

Key structures and state:
- `ocfs2_filecheck_errs[]` maps filecheck-specific status codes to strings.
- `struct ocfs2_filecheck_entry` records inode number, operation type, completion bit, and status.
- `struct ocfs2_filecheck_args` stores parsed sysfs input for check/fix inode numbers or queue-size updates.
- Each mount has `struct ocfs2_filecheck_sysfs_entry` with a kobject and `struct ocfs2_filecheck` queue state.

Major logic:
- Creates a `filecheck` kobject with `check`, `fix`, and `set` attributes under the per-device sysfs area.
- `show` for `set` returns the maximum queue size; `show` for `check` or `fix` prints matching queued entries with inode, done flag, and error string.
- `store` parses a positive integer argument, adjusts queue maximum for `set`, or enqueues a check/fix request for an inode.
- Queue management prevents duplicate pending entries, enforces min/max queue sizes, and evicts oldest completed entries when full.
- `ocfs2_filecheck_handle()` runs the actual check/fix by calling `ocfs2_iget()` with filecheck flags and maps returned statuses to filecheck errors.
- Removal deletes the kobject, waits for release completion, then frees completed queue entries.

Important entry points:
- `ocfs2_filecheck_create_sysfs()`
- `ocfs2_filecheck_remove_sysfs()`

Concurrency and lifetime:
- Queue state is protected by `fc_lock`.
- Sysfs show/store wrappers take a kobject reference around attribute callbacks.
- Kobject release signals a completion so mount teardown can wait before freeing backing state.
- Freeing asserts all entries are done.

Important dependencies:
- Uses OCFS2 inode loading/check flags, OCFS2 superblock device kset, kobject/sysfs infrastructure, spinlocks, and masklog.

Risk and edge cases:
- `ocfs2_filecheck_args_get_long()` copies `count` bytes into a fixed stack buffer after caller enforces `count < 24`; that validation is essential.
- Filecheck work is synchronous in the sysfs store path after enqueueing, so a slow inode check can delay the write.
- Queue resizing refuses to drop pending entries and only erases completed ones.
- Error-string lookup BUGs on out-of-range nonzero filecheck status values.
