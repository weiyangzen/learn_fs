# sources/security-integrity/selinux/libsemanage/src/boolean_internal.h

Purpose: internal aggregation header for boolean record and database backend implementations. It connects the public boolean APIs to the generic database framework.

Important APIs/types/functions: declares `SEMANAGE_BOOL_RTABLE` and init/release pairs for file, policydb, and active boolean databases: `bool_file_dbase_init`, `bool_policydb_dbase_init`, and `bool_activedb_dbase_init`.

Control flow: backend setup code includes this header, initializes the appropriate `dbase_config_t`, then the public boolean APIs route through generic database wrappers to the selected backend.

State and persistence behavior: no state in the header, but the declared backends cover persistent local boolean files, policydb boolean declarations, and active kernel boolean state. Release functions free backend-specific cache/config allocations.

Dependencies and integration points: includes public boolean local/policy/active headers plus `database.h` and internal `handle.h`. It is the coordination point for `boolean_record.c`, `booleans_file.c`, `booleans_policydb.c`, and `booleans_activedb.c`.

Risks: backend table mismatches would surface as incorrect CRUD behavior across all boolean APIs. Test signals include all three boolean views initializing, querying, listing, and releasing without leaks or cross-view confusion.
