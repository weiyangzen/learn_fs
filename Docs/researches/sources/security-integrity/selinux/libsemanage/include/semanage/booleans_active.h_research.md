# sources/security-integrity/selinux/libsemanage/include/semanage/booleans_active.h

Purpose: declares access to active kernel boolean state, which is distinct from local default boolean customizations and policydb boolean declarations.

Important APIs/types/functions: exports `semanage_bool_set_active`, `query_active`, `exists_active`, `count_active`, `iterate_active`, and `list_active` over `semanage_bool_key_t` and `semanage_bool_t`. `set_active` changes the live value; the remaining functions inspect active booleans.

Control flow: callers connect a handle, construct a boolean key, and read or update active state. Implementations route through an active-database backend that reads SELinux active boolean names and commits a complete boolean list back to libselinux.

State and persistence behavior: active boolean updates target the running system state and are not the same as persistent local policy defaults. The active database caches a list during operations and writes values through the active backend when flushed.

Dependencies and integration points: depends on the boolean record API and the handle abstraction; integrates with `booleans_active.c`, `booleans_activedb.c`, libselinux active boolean calls, and tools that need immediate boolean toggles.

Risks: callers can confuse active values with persistent local values. Complete-list commits must preserve unrelated booleans. Test signals include live boolean query/set behavior, count/list parity with SELinux active state, and no persistence unless corresponding local defaults are also modified.
