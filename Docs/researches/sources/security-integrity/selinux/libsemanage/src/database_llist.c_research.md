# sources/security-integrity/selinux/libsemanage/src/database_llist.c

Purpose: provides the common in-memory linked-list cache implementation for generic database backends.

Important APIs/types/functions: implements cache prepend/drop/resync serial, exists/add/set/modify/count/query/iterate/delete/clear/list, and helper cache lookup over `cache_entry_t` nodes.

Control flow: operations locate records by comparator, clone input records into cache entries, update links and size, mark modification state, and return cloned records for query/list. `add` prepends without duplicate checks; `modify` replaces or adds; `set` requires existing records.

State and persistence behavior: owns cloned record data in linked nodes, cache size, cache serial, and modified flag. It does not write durable storage; higher backends use it before flushing to files, active state, or policydb.

Dependencies and integration points: used by file, active, join, and policydb caching paths. Relies on object-specific record tables for clone, free, and comparison semantics.

Risks: list mutation and ownership are central; double-free or stale links would affect every backend. Test signals include CRUD ordering, modified flag transitions, query/list clone ownership, delete head/tail/middle cases, and cache drop cleanup.
