# File Research: sources/os/linux/linux/fs/ocfs2/filecheck.c

Online OCFS2 file-check sysfs implementation. It exposes per-mount sysfs controls that let privileged users request a check or fix of a specific inode and inspect recent results.

Sysfs layout:
- Creates a `filecheck` kobject under the OCFS2 device kset.
- Attributes:
  - `check`: write inode number to run check mode; read result list for check entries.
  - `fix`: write inode number to run fix mode; read result list for fix entries.
  - `set`: write max retained entry count; read current max.

Data model:
- `struct ocfs2_filecheck` owns a spinlock, entry list, maximum entries, current size, and done count.
- `struct ocfs2_filecheck_entry` records inode number, operation type, done bit, and filecheck status.
- Entry retention defaults to `OCFS2_FILECHECK_MINSIZE` and is bounded by `OCFS2_FILECHECK_MAXSIZE`.

Lifecycle:
- `ocfs2_filecheck_create_sysfs()` allocates state, initializes list/lock/counters, initializes the kobject, and adds sysfs files.
- `ocfs2_filecheck_remove_sysfs()` removes the kobject, waits for release completion, then frees only completed entries and the state object.
- `ocfs2_filecheck_release()` completes unregister synchronization.

Input parsing:
- Attribute type is inferred from name: `check`, `fix`, or `set`.
- Writes parse a positive integer from a bounded buffer.
- `set` adjusts maximum queue length only if pending entries still fit.

Queue behavior:
- Duplicate pending inode entries are rejected with `-EEXIST`.
- If the queue is full and no completed entry can be discarded, writes return `-EAGAIN`.
- If full with completed entries present, the oldest completed entry is erased to make room.
- New check/fix entries are inserted as `INPROGRESS`, then handled synchronously.

Check/fix execution:
- `ocfs2_filecheck_handle()` calls `ocfs2_iget()` with either `OCFS2_FI_FLAG_FILECHECK_CHK` or `OCFS2_FI_FLAG_FILECHECK_FIX`.
- Recognized OCFS2 filecheck-specific error codes are preserved; unexpected iget failures collapse to generic `FAILED`.
- Successful iget immediately drops the inode with `iput()`.
- Unsupported operation types report `UNSUPPORTED`.

Output:
- `check` and `fix` reads print a header plus matching entries with inode, done flag, and symbolic error string.
- `set` reads print the current max retained entries.

Important invariants and risks:
- The list is spinlock-protected; sysfs show/store takes a kobject reference around callbacks.
- Teardown asserts all entries are done before freeing.
- The actual validation/fix work is delegated to inode read paths through filecheck flags, so this file is mostly control-plane and result retention.
