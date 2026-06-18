# sources/security-integrity/selinux/libsemanage/src/database_join.c

Purpose: implements a virtual database that joins two component databases into one record view and splits modifications back into the components.

Important APIs/types/functions: `dbase_join_cache`, `dbase_join_flush`, `dbase_join_init`, `dbase_join_release`, and `SEMANAGE_JOIN_DTABLE`; uses a `record_join_table_t` with `join` and `split` callbacks.

Control flow: cache loads both component databases, merges ordered records by key, joins matching or single-sided entries, and stores joined records in a linked-list cache. Flush splits each joined record into component records, clears the component databases, repopulates them, and flushes components separately.

State and persistence behavior: the join cache is derived state. Persistence happens only through split records written to the underlying component dbases during flush.

Dependencies and integration points: depends on `database_llist`, generic component `dbase_config_t`s, and record comparators. Used where public records span base and extra local data, notably SELinux users.

Risks: comparator consistency across joined record types is essential. Split/flush errors can leave component caches modified but not durable. Test signals include one-sided joins, matching joins, sorted list output, component clear/repopulate, and rollback/drop-cache behavior.
