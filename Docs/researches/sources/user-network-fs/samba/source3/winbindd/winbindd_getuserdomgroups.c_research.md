# sources/user-network-fs/samba/source3/winbindd/winbindd_getuserdomgroups.c

## Purpose
Implements async `WINBINDD_GETUSERDOMGROUPS`, returning the domain group SID token for a user SID without aliases.

## Important APIs, Types, And Control Flow
`winbindd_getuserdomgroups_send()` parses the textual SID and calls `wb_gettoken_send(state, ev, &sid, false)`. The callback receives `num_sids` and `sids`. Recv formats each SID into a newline-separated string in response extra data and sets `num_entries`.

## State And Persistence
No local persistent state. Token generation and caching occur in `wb_gettoken`.

## Dependencies And Integration Points
Uses SID parsing, `wb_gettoken`, `dom_sid_str_buf`, and winbind extra-data string response conventions.

## Risks And Test Signals
Test invalid SID syntax, unknown users, users with no domain groups, nested groups, large tokens, and ensure `include_aliases=false` differs from `GETUSERSIDS`.
