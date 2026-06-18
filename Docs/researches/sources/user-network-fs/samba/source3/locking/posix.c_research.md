<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/posix.c -->
# sources/user-network-fs/samba/source3/locking/posix.c

## Purpose
`posix.c` maps Samba byte-range locks onto underlying kernel POSIX locks and manages deferred file descriptor closes required by process-scoped POSIX locking semantics. It supports both Windows-flavour SMB locks and POSIX-flavour SMB locks.

## Important APIs, Types, And Functions
Public APIs are `is_posix_locked`, `posix_locking_init`, `posix_locking_end`, `fd_close_posix`, `set_posix_lock_windows_flavour`, `release_posix_lock_windows_flavour`, `set_posix_lock_posix_flavour`, and `release_posix_lock_posix_flavour`. Important helpers include `map_posix_lock_type`, `posix_lock_in_range`, `posix_fcntl_lock`, `posix_fcntl_getlock`, reference-count helpers over `posix_pending_close_db`, `add_fd_to_close_entry`, `posix_lock_list`, `increment_posix_lock_count`, `decrement_posix_lock_count`, and `locks_exist_on_context`.

## Control Flow
Requests first map SMB lock type to `F_RDLCK` or `F_WRLCK`, downgrading write locks for read-only file opens. Range conversion rejects zero-length POSIX locks and clamps 64-bit SMB ranges into the host `off_t` range; unmappable ranges are treated as successfully ignored. Windows-flavour lock acquisition computes subranges not already covered by this process's locks, applies `F_SETLK` to each, and backs out partial success on failure. Windows-flavour release computes unlock holes so remaining overlapping locks are preserved and may downgrade write locks to read locks before unlocking. POSIX-flavour acquisition maps directly; release punches holes around retained same-process locks. `fd_close_posix` defers closing fds while any lock refcount remains on the file id and later drains saved fds.

## State And Persistence
`posix_pending_close_db` is an in-memory rb-tree dbwrap database. It stores lock refcounts keyed by `file_id + 'r'`, pending close fd arrays keyed by `file_id`, and POSIX context markers keyed by `smblctx`. This state is process-local, not durable, and exists to avoid POSIX lock release side effects when closing one fd would drop locks held through another fd.

## Dependencies And Integration Points
The file depends on VFS lock/getlock hooks, `files_struct` fd helpers, Samba `file_id`, server ids, dbwrap rb-tree storage, and configuration flags `lp_locking`, `lp_posix_locking`, and `use_ofd_locks`. It is called from `brlock.c` when byte-range locks need lower-level POSIX enforcement and from fd close paths.

## Risks And Test Signals
The range-splitting and hole-punching logic is subtle and must preserve Windows reference-count semantics over non-reference-counted POSIX locks. Treating unmappable high ranges as success is compatibility-driven but can hide enforcement gaps. The context-marker key only contains `smblctx`, so uniqueness assumptions matter. Pending-close state stores raw fds and must not double-close or leak them. Test signals include overlapping read/write locks across fds, downgrade-on-unlock cases, 32-bit/NFS large-offset fallbacks, OFD-lock bypass, deferred close drain, POSIX CIFS unlock holes, and failure rollback after partial `F_SETLK` success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/posix.c -->
