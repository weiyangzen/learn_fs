# sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getmembers.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/localgroup/localgroup_getmembers.c

Purpose: Demonstrates paged enumeration of local group members with `NetLocalGroupGetMembers()`.

Important APIs/types/functions: Supports levels 0, 1, 2, and 3. Prints SIDs with `sid_string_tos()`, SID usage, resolved names, and domain-qualified names.

Control flow: Parses hostname/group/level, loops over result pages with a resume handle, casts buffer by level, prints member fields, frees each page, and reports final errors.

State and persistence behavior: Read-only membership query.

Dependencies and integration points: Primary verifier for add/delete/set localgroup member examples.

Risks: SID conversion may fail and suppress SID text. Name resolution behavior depends on server/domain state.

Test signals: Query groups containing SID-only and resolved domain members at all supported levels.
