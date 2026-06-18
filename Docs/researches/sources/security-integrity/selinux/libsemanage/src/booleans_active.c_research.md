# sources/security-integrity/selinux/libsemanage/src/booleans_active.c

Purpose: implements the public active-boolean API by forwarding operations to the handle's active boolean database configuration.

Important APIs/types/functions: `semanage_bool_set_active`, `query_active`, `exists_active`, `count_active`, `iterate_active`, and `list_active` call `dbase_set`, `dbase_query`, `dbase_exists`, `dbase_count`, `dbase_iterate`, and `dbase_list`.

Control flow: each function retrieves `semanage_bool_dbase_active(handle)` and delegates to the generic database wrapper. Writes enter the active database write path; reads enter the read-only path.

State and persistence behavior: state is managed by the active database backend, which reads and commits complete active boolean lists. These calls affect live SELinux boolean state rather than local default files.

Dependencies and integration points: includes the public active header, `boolean_internal.h`, and `database.h`; integrates with `booleans_activedb.c` and libselinux active boolean APIs through the backend.

Risks: thin forwarding leaves correctness dependent on active backend initialization and wrapper transaction checks. Test signals are active set/query/list calls and error propagation from inaccessible SELinux active state.
