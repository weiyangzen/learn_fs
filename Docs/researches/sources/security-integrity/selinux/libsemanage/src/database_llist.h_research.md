# sources/security-integrity/selinux/libsemanage/src/database_llist.h

Purpose: declares the linked-list cache structure and helpers shared by multiple database backends.

Important APIs/types/functions: defines `cache_entry_t`, `dbase_llist_t`, inline init/modified/rtable helpers, and exported cache/drop/CRUD/list functions.

Control flow: backend init embeds or allocates a `dbase_llist_t`, initializes it with a record table and dbase table, then delegates generic operations to this helper layer.

State and persistence behavior: tracks `cache`, `cache_tail`, `cache_sz`, `cache_serial`, and `modified`. Persistent storage is outside this layer; serials detect resync needs after commits.

Dependencies and integration points: includes `database.h` and `handle.h`; used by `database_file.c`, `database_activedb.c`, `database_join.c`, and `database_policydb.c`.

Risks: all callers depend on consistent modified and serial behavior. Test signals include init/drop idempotence, serial refresh, and cache size correctness after each mutation.
