# sources/user-network-fs/samba/source3/winbindd/wb_alias_members.c

## Purpose
This async helper retrieves members of an alias SID through winbind child RPC, with a cached usergroups fast path and a max-nesting guard.

## Important APIs, Types, And Functions
`struct wb_alias_members_state` stores the event context, target SID, and resulting `wbint_SidArray`. Public APIs are `wb_alias_members_send` and `wb_alias_members_recv`; callback `wb_alias_members_done` completes the child RPC.

## Control Flow
The send function validates `max_nesting`; at zero or below it returns an empty SID array immediately. It copies the SID, tries `lookup_usergroups_cached`, then locates the domain with `find_domain_from_sid_noinit`. If found, it calls `dcerpc_wbint_LookupAliasMembers_send` against the domain child handle. The callback combines transport/result status and completes. The recv function moves the SID array to the caller and logs results.

## State And Persistence
State is request-local. Cached membership can come from winbind cache through `lookup_usergroups_cached`; otherwise state is remote child RPC output.

## Dependencies And Integration
It integrates with tevent, generated winbind RPC stubs, domain lookup, child binding handles, SID helpers, and debug logging. `wb_getgrsid.c` uses it for alias group member expansion.

## Risks And Test Signals
Test max nesting zero, cache hit, unknown domain, child RPC transport failure, child result failure, empty alias, and memory ownership of returned SIDs. Cached usergroup semantics should match direct alias lookup or callers can observe inconsistent expansion.
