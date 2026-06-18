<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_builtin.c -->
# sources/user-network-fs/samba/source3/lib/util_builtin.c

## Purpose
`util_builtin.c` maps Windows BUILTIN domain RIDs to names and provides predicates for BUILTIN SIDs.

## Important APIs, types, and functions
`struct rid_name_map` and `builtin_aliases` define known built-in aliases such as Administrators, Users, Guests, Backup Operators, Remote Desktop Users, and Event Log Readers. Public APIs are `lookup_builtin_rid`, `lookup_builtin_name`, `builtin_domain_name`, `sid_check_is_builtin`, `sid_check_is_in_builtin`, and `sid_check_is_wellknown_builtin`.

## Control flow
Lookup functions linearly scan the static alias table. SID predicates compare the full SID with `global_sid_Builtin`, or copy and split the RID before checking domain and known RID membership.

## State and persistence behavior
All data is static and read-only. Returned names from RID lookup are talloc duplicates owned by the caller.

## Dependencies and integration points
The file depends on Samba security SID helpers and global SID constants. It feeds passdb, access checks, id mapping, and SID/name display logic.

## Risks and edge cases
The alias table must stay aligned with Windows well-known BUILTIN RIDs. `sid_check_is_in_builtin` treats any SID under S-1-5-32 as in BUILTIN, while `sid_check_is_wellknown_builtin` restricts to table entries.

## Test signals
Tests should verify bidirectional RID/name lookup, case-insensitive name matching, domain SID checks, and unknown RID rejection by `sid_check_is_wellknown_builtin`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_builtin.c -->
