# sources/user-network-fs/samba/source3/winbindd/wb_gettoken.c

## Purpose
This async helper builds an access-token SID list for a user: user SID, primary group SID, domain groups, optional local aliases, and builtin aliases.

## Important APIs, Types, And Functions
`struct wb_gettoken_state` stores event context, user SID, `expand_local_aliases`, and the growing SID array. Public APIs are `wb_gettoken_send` and `wb_gettoken_recv`. `wb_add_rids_to_sids` composes alias RIDs into domain SIDs and adds them uniquely.

## Control Flow
The send function queries user info. The first callback seeds the SID array with user and primary group SIDs and calls `wb_lookupusergroups_send`. Group lookup failures are tolerated by completing with the seed SIDs. Successful groups are added uniquely. If local alias expansion is disabled, the request completes. Otherwise it queries aliases in the local SAM domain, adds resulting RIDs as SIDs, then queries builtin aliases and adds those RIDs before completing.

## State And Persistence
State is request-local. The SID array grows through talloc reallocation by `add_sid_to_array_unique`; no durable state is written.

## Dependencies And Integration
It depends on `wb_queryuser`, `wb_lookupusergroups`, `wb_lookupuseraliases`, local SAM SID helpers, builtin SID, and uniqueness helpers. It feeds auth/token construction paths.

## Risks And Test Signals
Test queryuser failure, lookupusergroups failure tolerance, duplicate group/alias SIDs, local alias expansion disabled/enabled, missing local or builtin domains, alias lookup failures, and large SID arrays. The local group step uses `find_domain_from_sid_noinit(get_global_sam_sid())`; startup/domain-list timing can affect behavior.
