# File Research: sources/teaching/os161/kern/vfs/vnode.c

Implements generic vnode lifecycle and validation. `vnode_init` installs the ops table, initializes refcount to one, initializes the refcount spinlock, and stores filesystem and private data. `vnode_cleanup` asserts refcount is one, cleans the spinlock, and poisons logical ownership fields to null/zero.

`vnode_incref` increments under `vn_countlock`. `vnode_decref` decrements when refcount is greater than one; when dropping the last reference it leaves the count for `VOP_RECLAIM`, calls reclaim outside the spinlock, and warns on unexpected errors other than `EBUSY`.

`vnode_check` validates non-null/non-poison pointers, ops magic, filesystem pointer sanity, and refcount range before every `VOP_*` dispatch.
