# sources/security-integrity/selinux/libsemanage/src/booleans_activedb.c

Purpose: implements the active boolean database backend, adapting libselinux active boolean state to the generic linked-list database API.

Important APIs/types/functions: defines `bool_read_list`, `bool_commit_list`, `SEMANAGE_BOOL_ACTIVEDB_RTABLE`, `bool_activedb_dbase_init`, and `bool_activedb_dbase_release`.

Control flow: `bool_read_list` calls `security_get_boolean_names`, allocates semanage boolean records, sets names and active values with `security_get_boolean_active`, and returns an array. `bool_commit_list` converts records to name/value arrays and calls `security_set_boolean_list`. Init wraps the read/commit functions in `dbase_activedb_init`.

State and persistence behavior: the backend caches active booleans in memory through the generic active database. Flush writes the full list back to the running SELinux kernel state; it is not a persistent local-policy write.

Dependencies and integration points: depends on libselinux active boolean APIs, `SEMANAGE_BOOL_RTABLE`, `database_activedb`, and semanage error reporting.

Risks: partial allocation failures require freeing names, values, records, and arrays. Full-list commits can overwrite concurrent active changes. Test signals include accurate count/list, set-active round trips, failure cleanup, and behavior when SELinux is disabled or inaccessible.
