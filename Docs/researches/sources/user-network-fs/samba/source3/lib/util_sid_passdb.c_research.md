<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.c -->
# sources/user-network-fs/samba/source3/lib/util_sid_passdb.c

## Purpose
`util_sid_passdb.c` decides whether a SID or SID domain should be handled by Samba passdb/idmapping according to configured passdb responsibility.

## Important APIs, types, and functions
Public APIs are `sid_check_object_is_for_passdb` for object SIDs and `sid_check_is_for_passdb` for object-or-domain SIDs.

## Control flow
Both functions test SID families in priority order: our SAM, BUILTIN, well-known domain, Unix users, Unix groups, and a catch-all responsibility. The object-only function checks in-domain object predicates; the broader function also accepts exact domain SIDs such as our SAM, BUILTIN, well-known, Unix users, and Unix groups.

## State and persistence behavior
The functions are pure predicates over input SID and passdb responsibility state. They do not modify passdb.

## Dependencies and integration points
They depend on special SID predicates, machine SID helpers, Unix SID helpers, and passdb responsibility flags such as `pdb_is_responsible_for_builtin`. Idmap and account lookup code use them to route SID handling.

## Risks and edge cases
Ordering matters when the catch-all responsibility is enabled because it returns true for otherwise unrecognized SIDs. Object-only versus domain-inclusive semantics must be chosen correctly by callers.

## Test signals
Tests should cover each SID family with corresponding responsibility flag enabled/disabled, exact domain SID versus object SID behavior, and the everything-else fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sid_passdb.c -->
