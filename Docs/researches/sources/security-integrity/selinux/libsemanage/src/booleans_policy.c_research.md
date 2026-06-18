# sources/security-integrity/selinux/libsemanage/src/booleans_policy.c

Purpose: implements public policy boolean read APIs by forwarding to the policy boolean database.

Important APIs/types/functions: `semanage_bool_query`, `exists`, `count`, `iterate`, and `list` wrap generic database read operations on `semanage_bool_dbase_policy(handle)`.

Control flow: connected callers invoke a policy read function, the wrapper enters the read-only database path, caches/resyncs the policy backend as needed, and returns cloned boolean records or counts.

State and persistence behavior: read-only observation of boolean declarations and defaults in the policydb. It may fill caches but never writes store files.

Dependencies and integration points: connects public `booleans_policy.h` to `booleans_policydb.c` through `database.c` wrappers. Used by management tools and validators that need base policy state.

Risks: stale cache detection depends on database serials. Test signals include query/list parity with policydb contents, iterate callback behavior, and correct visibility after rebuild.
