# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_specificdata.c

Read completely: 415 lines.

This file implements NetBSD's generic "specific data" facility: domains own numbered keys, and individual objects hold a `specificdata_reference` pointing to a per-object container of `void *` slots. It is the kernel-side analogue of keyed per-object private data.

Core structures: `specificdata_domain` holds the domain mutex, key count, live container list, and destructor table. `specificdata_container` stores a variable-length slot array and is linked into the domain so key deletion can visit all containers. `specificdata_key_impl` stores the key destructor.

Key operations:
- `specificdata_domain_create` allocates a domain and initializes its lock/list.
- `specificdata_key_create` finds a free key slot or grows the key table, substituting a no-op destructor when callers pass `NULL`.
- `specificdata_key_delete` runs the key destructor over every container and marks the key unused.
- `specificdata_init`/`specificdata_fini` initialize and destroy a per-object reference.
- `specificdata_getspecific` reads a key under the reference lock; `_unlocked` is an explicitly unsafe fast path.
- `specificdata_setspecific` lazily allocates or resizes a container to the domain's current key count, links it into the domain list, and swaps it into the reference.

Locking/integration: the file documents a strict lock order of domain lock before reference lock for writes to `specdataref_container`. Readers need either domain or reference lock. Resizing follows that rule on the slow path and frees the old container after publishing the new one.

Reliability notes: `specificdata_domain_delete` is intentionally unimplemented and panics. `specificdata_key_create` allocates while holding the domain lock, marked by an `XXXSMP` comment. Destructors run while the domain lock is held, so destructor behavior must avoid re-entering this domain in ways that deadlock.
