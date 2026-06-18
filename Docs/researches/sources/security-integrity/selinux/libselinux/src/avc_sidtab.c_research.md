# sources/security-integrity/selinux/libselinux/src/avc_sidtab.c

Purpose: `avc_sidtab.c` implements the userspace AVC SID table: a hash table that interns raw security context strings and returns stable `security_id_t` pointers for cache keys and audit formatting.

Important APIs/types/functions: `sidtab_init()` allocates buckets, `sidtab_context_lookup()` finds an existing `security_id`, `sidtab_context_to_sid()` inserts if missing, `sidtab_sid_stats()` reports bucket utilization, and `sidtab_destroy()` frees contexts and nodes. `sidtab_hash()` is a djb2-style hash masked to 128 buckets.

Control flow: lookups hash a context and traverse a bucket chain by `strcmp`. Insertions allocate a node through `avc_malloc()`, duplicate the context with `strdup()`, assign a monotonically increasing integer ID, and prepend to the selected bucket.

State and persistence: each table owns allocated bucket array and nodes. Entries persist until `sidtab_destroy()`, and pointers are used by the AVC cache, so they must not be freed during live cache operation.

Dependencies and integration: uses `avc_internal` allocation wrappers, `freecon()` for duplicated contexts, and public AVC `struct security_id`.

Risks and test signals: failure paths must leave `*sid = NULL` on insert failure. The table stops at `UINT_MAX - 1` entries. Tests should cover duplicate lookup returning identical pointer, collision chains, stats formatting, allocation failure, and destroy with null/empty tables.
