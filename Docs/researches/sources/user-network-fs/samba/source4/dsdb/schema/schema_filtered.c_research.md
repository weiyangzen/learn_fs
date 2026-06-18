# sources/user-network-fs/samba/source4/dsdb/schema/schema_filtered.c

## Purpose
`schema_filtered.c` decides whether a schema attribute is eligible for inclusion in a filtered replica, such as RODC filtered attribute set behavior.

## Important APIs, Types, and Functions
The policy list `never_in_filtered_attrs` names attributes that must not be in a filtered replica, including secret attributes via `DSDB_SECRET_ATTRIBUTES`. The exported predicate is `dsdb_attribute_is_attr_in_filtered_replica`.

## Control Flow and Behavior
The predicate rejects attributes that are `systemOnly`, critical by `schemaFlagsEx`, not replicated, required partial-set members, constructed, explicitly listed in `never_in_filtered_attrs`, or marked with `SEARCH_FLAG_RODC_ATTRIBUTE`. Anything else is considered eligible.

## State and Persistence Behavior
No state is persisted. The function reads immutable fields from a loaded `dsdb_attribute`; the policy list is static compile-time data.

## Dependencies and Integration Points
It depends on schema attribute structures, DSDB flag definitions, secret attribute macros, and search/schema flag constants. It integrates with replication and schema-management paths that validate or compute filtered attribute sets.

## Risks and Edge Cases
The deny list is exact string comparison and case-sensitive, unlike many LDAP attribute comparisons. Policy correctness depends on the static list staying aligned with Windows and Samba semantics. New secret or operational attributes must be added here or rejected through flags.

## Test Signals
Tests should cover each flag-based rejection, deny-list entries, secret attributes expansion, RODC attribute flag, ordinary eligible attributes, and case-variant attribute names if schema loading can preserve unusual case.
