# File Research: sources/os/bsd/freebsd-src/sys/fs/nullfs/null_subr.c

This file implements nullfs vnode alias caching: mapping a lower vnode plus upper mount to a unique nullfs vnode.

Key responsibilities:
- Initializes and destroys the nullfs hash table, hash lock, and SMR-enabled UMA node zone.
- Looks up existing aliases with `null_hashget()` and `null_hashget_locked()`.
- Creates or returns an existing alias vnode in `null_nodeget()`.
- Inserts and removes `struct null_node` entries from the hash.
- Provides diagnostic lower-vnode validation via `null_checkvp()`.

Core flow in `null_nodeget()`:
1. Requires the lower vnode locked and referenced.
2. Checks the hash for an existing alias; if found, releases the caller’s spare lower vnode reference and returns the alias.
3. Allocates a `null_node` and `getnewvnode()` using either normal or no-UNP-bypass vnode ops.
4. Sets upper vnode type, `v_data`, shared lock pointer (`v_vnlock = lowervp->v_vnlock`), page-read/inotify flags, and root flag when appropriate.
5. Rechecks for duplicates under `null_hash_lock`.
6. Inserts the vnode into the mount queue and hash, then marks it constructed.

Concurrency/lifetime details:
- Hash lookups use VFS SMR for lockless reads.
- Insert/remove use a global rwlock.
- Duplicate creation is tolerated and resolved under the write lock.
- `null_destroy_proto()` tears down a just-created duplicate/prototype vnode and frees its node via SMR.
- Lower vnode references are transferred into the nullfs node on successful creation.

Research-relevant risks:
- The code relies on the lower vnode lock to prove found aliases are not doomed during lookup.
- `null_nodeget()` has delicate ownership semantics: callers pass a locked lower vnode with a spare reference, which is consumed on success.
- Page cache and inotify flags are copied opportunistically and may be rechecked later by open paths.
