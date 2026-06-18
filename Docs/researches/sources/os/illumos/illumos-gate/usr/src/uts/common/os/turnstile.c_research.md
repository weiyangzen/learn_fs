# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/turnstile.c

Implements turnstiles: the kernel blocking, wakeup, and priority-inheritance mechanism used by synchronization primitives such as mutexes, rwlocks, and user priority-inheritance locks.

Key responsibilities:
- Maintains a global hash table mapping synchronization-object addresses to active turnstiles.
- Lets the first waiter donate its per-thread turnstile and later waiters chain their turnstiles on the active turnstile freelist.
- Tracks reader and writer sleep queues per turnstile.
- Walks blocking chains to propagate priority inheritance and prevent unbounded priority inversion.
- Supports direct handoff wakeups where a woken thread inherits priority before it runs.
- Provides special interruptible behavior for `SOBJ_USER_PI` locks.

Important paths:
- `turnstile_lookup()` locks the hash bucket and returns the active turnstile for a synchronization object.
- `turnstile_block()` installs or joins an active turnstile, marks the thread sleeping, inserts it into the selected sleep queue, walks owners to apply priority inheritance, handles user-PI cycles as `EDEADLK`, and switches away.
- `turnstile_interlock()` handles difficult lock ordering when both waiter and owner locks are turnstile locks, using address order and a loser lock to avoid deadlock and livelock.
- `turnstile_wakeup()` waives inherited priority from the releasing owner, dequeues one or more waiters, performs scheduler-class wakeups, and applies inheritance to a direct-handoff owner when applicable.
- `turnstile_dequeue()` removes a waiter, returns or reassigns turnstile structures, removes inactive turnstiles from the hash chain, and clears thread wait-channel state.
- `turnstile_unsleep()` supports interrupting user-PI waiters without immediate disinherit; owners must later call `turnstile_pi_recalc()`.

Locking and invariants:
- Each turnstile hash bucket has a dispatcher lock that also protects the waiters bits of synchronization objects hashing to that bucket.
- Clients may manipulate waiters indicators and certain owner transitions only while under `turnstile_lookup()`.
- The implementation assumes clients never block on unheld locks.
- User-PI locks require special handling because an `upimutextab[]` lock is held until the thread has blocked and willed priority.

Filesystem relevance:
- Filesystems do not generally call this file directly, but mutexes and rwlocks used throughout VFS, vnode, VM, page-cache, and storage code depend on turnstiles for blocking correctness and priority inheritance under contention.
