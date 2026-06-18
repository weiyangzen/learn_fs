# sources/user-network-fs/samba/source3/winbindd/winbindd_getgroups.c

## Purpose
Implements async `WINBINDD_GETGROUPS`, returning the Unix GID list for a named user's token.

## Important APIs, Types, And Control Flow
The send path runs parent idmap setup, unmaps normalized names, parses namespace/domain/user, and looks up the user SID with `LOOKUP_NAME_NO_NSS`. `winbindd_getgroups_lookupname_done()` calls `wb_gettoken_send(..., true)` to include the user SID and groups. `winbindd_getgroups_gettoken_done()` maps the complete SID token with `wb_sids2xids_send()`. The mapping callback converts acceptable `ID_TYPE_GID` and `ID_TYPE_BOTH` entries to GIDs, permits the user SID only if not an inappropriate UID, logs skipped entries, shrinks the gid array, and completes. Recv returns the gid array in extra data.

## State And Persistence
No persistent writes. It depends on idmap setup cache and token/cache state below helper calls.

## Dependencies And Integration Points
Uses idmap setup, wbint normalization, `parse_domain_user`, `wb_lookupname`, `wb_gettoken`, `wb_sids2xids`, and `passdb/lookup_sid.h` for `LOOKUP_NAME_NO_NSS`.

## Risks And Test Signals
Security-sensitive risk is skipped IDs from DENY ACE-related groups; the code logs warnings when idmap types are unusable. Test unmapped groups, UID-only mappings in group positions, ID_TYPE_BOTH, no groups, large tokens, normalized UPN/domain names, and `STATUS_SOME_UNMAPPED` conversion to success.
