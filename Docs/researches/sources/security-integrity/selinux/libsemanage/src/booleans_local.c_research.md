# sources/security-integrity/selinux/libsemanage/src/booleans_local.c

Purpose: implements public local boolean CRUD as thin wrappers over the generic local boolean database.

Important APIs/types/functions: exports `semanage_bool_modify_local`, `del_local`, `query_local`, `exists_local`, `count_local`, `iterate_local`, and `list_local`.

Control flow: each function obtains `semanage_bool_dbase_local(handle)` and forwards to `dbase_modify`, `dbase_del`, `dbase_query`, `dbase_exists`, `dbase_count`, `dbase_iterate`, or `dbase_list`.

State and persistence behavior: modifications update the local boolean override cache and are persisted through the normal semanage transaction commit. Reads observe the local defaults, not necessarily live active values.

Dependencies and integration points: depends on `boolean_internal.h` and `database.h`; participates in direct commit where local boolean changes are merged into the policydb/kernel policy.

Risks: all behavioral validation is delegated to the database and record layers. Test signals include local default add/delete/query, commit merge into kernel policy, and distinction from active boolean operations.
