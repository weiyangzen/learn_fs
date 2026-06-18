# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/xfile.c

Qid/session and user-fid cache for 9nfs file objects.

Key responsibilities:
- `xfile()` finds, creates, or removes `Xfile` objects keyed by qid path and session pointer.
- `xfid()` finds, creates, or removes per-user `Xfid` objects under an `Xfile`.
- Removed `Xfid` entries clunk associated user/root and open fids.
- `xfpurgeuid()` clears all cached fids for a user within a session.

Important behavior:
- `xfile()` uses 127 hash buckets protected by per-bucket locks.
- Recently-used file/fid entries are moved to the front of their lists.
- Free lists are batch-allocated with `listalloc()`.

Dependencies:
- Uses `Xfile`, `Xfid`, `Session`, `Qid`, `clunkfid()`, `xfclear()`, and string interning.

Notable risks:
- Hashing casts session pointers down through `u32int`, which is architecture-sensitive.
- `xfid()` itself is not locked; callers must rely on surrounding `Xfile`/session locking discipline.
