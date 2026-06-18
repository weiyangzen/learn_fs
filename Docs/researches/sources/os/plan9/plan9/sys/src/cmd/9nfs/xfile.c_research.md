# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/xfile.c

Cached NFS-export file and per-user fid table.

Key responsibilities:
- `xfile` hashes `(qid->path, session pointer)` into 127 buckets and returns, creates, or removes an `Xfile`.
- Moves recently used `Xfile` records to the bucket front.
- `xfid` manages per-user state hanging off an `Xfile`, including user root and open fids.
- Removal of an `Xfid` clunks active 9P fids before recycling.
- `xfpurgeuid` clears all cached fids for a user within a session.

Dependencies:
- Uses `Qid`, `Xfile`, `Xfid`, `Session`, `Lock`, `listalloc`, `strstore`, `clunkfid`, and `xfclear`.
- Uses bucket locks for `xfile` and purge traversal.

Notable risks:
- Hashing truncates session pointers through `u32int`, reflecting old 32-bit assumptions.
- `xfid` itself is not internally locked; callers must protect per-file user lists where needed.
