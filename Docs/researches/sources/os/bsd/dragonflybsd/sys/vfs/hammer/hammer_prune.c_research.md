# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_prune.c

Purpose: implements the pruning ioctl that removes historical deleted records when their create/delete TIDs fall within retention windows supplied by userland.

Main flow: `hammer_ioc_prune()` validates the key range, rejects caller-supplied PFS localization bits, copies the prune element array from userland, derives scan localizations from the ioctl inode, and scans backward from `key_end` toward `key_beg`. Reverse iteration avoids creating overlapping records ahead of the scan when delete operations adjust B-tree boundaries.

Deletion decision: `prune_should_delete()` supports two modes. With `HAMMER_IOC_PRUNE_ALL`, any record with nonzero `delete_tid` is removed. Otherwise the caller supplies a descending list of prune windows, and a deleted record is removable only when `create_tid` and `delete_tid` fall within the same modulo bucket between `beg_tid` and `end_tid`.

Mutation behavior: deletions use `hammer_delete_at_cursor(... HAMMER_DELETE_DESTROY ...)` under the sync lock so the change remains within one flush group. Directory and non-directory record statistics are updated separately, and byte counts come from the delete call.

Extra cleanup: `prune_check_nlinks()` detects live inode records with zero link count, obtains and releases the inode, and lets inode reclamation clean dangling state that can result from crashes with deleted files still open.

Operational behavior: the loop honors read-only transition (`EROFS`), user interruption (`EINTR` converted to ioctl interrupt flag), B-tree deadlock retry, and flusher backpressure when metadata or UNDO space is tight. `key_cur` is normalized back to a type-only localization before returning to userland.
