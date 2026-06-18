# sources/user-network-fs/samba/source3/winbindd/winbindd_getusersids.c

## Purpose
Implements async `WINBINDD_GETUSERSIDS`, returning the complete SID token for a user SID, including aliases.

## Important APIs, Types, And Control Flow
`winbindd_getusersids_send()` null-terminates and parses `request->data.sid`, then calls `wb_gettoken_send(..., true)`. The callback stores the returned SID array. Recv builds a newline-separated SID string in response extra data and updates `num_entries`.

## State And Persistence
No persistent local state. Token expansion and domain/cache access are delegated to `wb_gettoken`.

## Dependencies And Integration Points
Uses security SID helpers, token helper APIs, and winbind textual extra-data output format.

## Risks And Test Signals
Test malformed SIDs, unknown users, alias inclusion, nested memberships, very large tokens, and memory failure during string accumulation. Compare with `GETUSERDOMGROUPS` to verify alias behavior.
