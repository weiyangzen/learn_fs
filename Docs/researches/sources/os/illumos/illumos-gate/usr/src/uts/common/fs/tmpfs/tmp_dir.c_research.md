# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/tmpfs/tmp_dir.c

Tmpfs directory-entry implementation: hashed lookup, directory list maintenance, create/link/rename/delete semantics, `.`/`..` initialization, and tmpnode creation helpers.

Key responsibilities:
- Maintains a global directory-entry hash table keyed by parent tmpnode and name, with 8192 buckets and 64 mutexes.
- Provides `tmpfs_hash_init`, `tmpfs_hash_in`, `tmpfs_hash_out`, `tmpfs_hash_change`, and `tmpfs_hash_lookup`.
- Implements `tdirlookup()` with execute permission checks and tmpnode holds on success.
- Implements `tdirenter()` for create, mkdir, link, and rename, including slash rejection, detached-directory handling, permission checks, link-count adjustment, and cleanup on partial failures.
- Implements `tdirdelete()` for remove, rename unlink, and rmdir, including sticky-directory checks, hash/list removal, ctime/mtime updates, link decrement, and directory truncation on rmdir.
- Initializes directories in `tdirinit()` by creating `.` and `..` entries, setting list offsets, link counts, and timestamps.
- Removes every entry in a directory via `tdirtrunc()`, with special xattr-directory link-count rules.
- Prevents directory rename cycles with `tdircheckpath()`.
- Replaces existing rename targets through `tdirrename()`, enforcing same-filesystem, type compatibility, empty-directory and mountpoint checks.
- Rewrites `..` on cross-directory renames via `tdirfixdotdot()`.
- Allocates and inserts directory entries in `tdiraddentry()`, using stable synthetic offsets and a roving slot pointer.
- Creates tmpnodes in `tdirmaketnode()`, including type, rdev, uid/gid inheritance, setgid handling, and initial directory setup.

Dependencies:
- Uses tmpnode and tmount structures from `sys/fs/tmpnode.h` and `sys/fs/tmp.h`.
- Uses permission helpers from `tmp_subr.c`, tmpnode allocation from `tmp_tnode.c`, and VFS/vnode event helpers.
- Uses vnode mount locks to prevent renaming/removing mounted directories.

Concurrency and locking:
- Directory mutation requires the target directory `tn_rwlock` held as writer.
- Link/rename may need the source tmpnode lock while already holding the target directory lock.
- Rename deadlock avoidance uses `rw_tryenter()`, drops/reacquires the target directory lock around `delay()`, and exposes tunables `tmpfs_rename_backoff_delay`, `tmpfs_rename_backoff_tries`, and `tmpfs_rename_loops`.
- Hash buckets have separate mutexes; `tmpfs_hash_change()` updates the tmpnode pointer under the appropriate hash mutex.

Notable risks:
- Link counts are deliberately adjusted before some operations and unwound on errors; mistakes can leak or prematurely free tmpnodes.
- Xattr directories have nonstandard link-count rules, especially for implicit `..` references.
- Synthetic directory offsets are not byte offsets; readdir users depend on their stability across removals.
- Rename replacement of directories must coordinate mountpoint locks, emptiness, `..` rewrites, and destination vnode events.
