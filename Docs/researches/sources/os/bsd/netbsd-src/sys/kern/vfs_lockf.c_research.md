# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_lockf.c

Read completely: 975 lines.

Implements NetBSD advisory byte-range locking for vnode-backed files, covering POSIX `fcntl` locks and BSD `flock`-style locks. Locks are stored as sorted `struct lockf` ranges hanging from a per-vnode head pointer, while a single global `lockf_lock` serializes lock-list mutation and deadlock checks.

Core structures and policy:
- `struct lockf` records lock type, range start/end, owner identity, lock semantics flags, list linkage, wait queues, condition variable, and cached `uidinfo`.
- `lf_next` is dual-purpose: for granted locks it links the vnode lock list; for blocked locks it points at the blocking lock whose `lf_blkhd` contains the waiter.
- EOF-extended locks use `lf_end == -1`.
- Lock allocation is charged to the effective uid through `ui_lockcnt`; non-root users are capped by `MAXLOCKSPERUID`, with special allowance for unlock-time splitting.
- The implementation intentionally uses a coarse global mutex; comments note that more parallelism would only matter under heavy byte-range lock contention.

Range matching and mutation:
- `lf_findoverlap()` walks sorted ranges and classifies six overlap cases: none, equal, existing contains requested, requested contains existing, existing starts before, or existing ends after.
- `lf_split()` splits an existing lock around a contained new/unlock range, consuming a preallocated spare lock when three pieces are required.
- `lf_clearlock()` removes or shrinks owned locks for `F_UNLCK`, waking waiters on affected ranges.
- `lf_wakelock()` drains a blocking queue, clears each waiter’s blocking pointer, and broadcasts its condition variable.
- `lf_getblock()` returns the first conflicting lock owned by another id, with shared/read locks allowed to coexist.

Lock acquisition behavior:
- `lf_setlock()` first checks for conflicting locks. Nonblocking requests fail with `EAGAIN`.
- Waiting POSIX locks perform bounded deadlock detection by following single-LWP process wait channels through lock wait chains, returning `EDEADLK` on cycles or excessive depth.
- Waiting `flock` exclusive locks first drop any shared locks held by the same owner to match flock upgrade semantics.
- Waiters sleep with `cv_wait_sig()` and clean themselves from block queues if interrupted.
- Once unblocked, the new lock is merged with, replaces, splits, or removes overlapping same-owner locks depending on overlap case and type changes.

External interface:
- `lf_advlock()` converts `struct flock` `whence/start/len` fields into normalized inclusive ranges, including `SEEK_END`, zero-length-to-EOF, and negative-length `lockf()` ranges.
- It preallocates the main lock and any needed spare lock before taking `lockf_lock`.
- Supports `F_SETLK`, `F_UNLCK`, and `F_GETLK`.
- `lf_getlock()` fills a `struct flock` with the blocking lock’s type, range, and pid, or returns `F_UNLCK` if no blocker exists.
- `lf_init()` initializes the subsystem mutex.

Risks and notes:
- Correctness depends on strict global-lock discipline around all lock-list and wait-queue operations.
- The owner API is still `void *`; comments note it should ideally expose POSIX owners as `struct proc *`.
- Deadlock detection is conservative and bounded; it skips multi-LWP processes and non-POSIX locks.
- Range arithmetic is overflow-checked in `lf_advlock()`, but EOF and negative-length cases remain subtle.
- Unlock operations may allocate even beyond the normal user cap so that range splitting can complete.
