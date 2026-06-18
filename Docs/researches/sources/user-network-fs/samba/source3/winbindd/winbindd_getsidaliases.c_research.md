# sources/user-network-fs/samba/source3/winbindd/winbindd_getsidaliases.c

## Purpose
Implements async `WINBINDD_GETSIDALIASES`, returning local/domain alias SIDs for an input domain SID and optional SID list.

## Important APIs, Types, And Control Flow
The send path parses `request->data.sid`, finds the owning domain with `find_domain_from_sid_noinit()`, optionally validates and parses newline/comma SID list extra data via `parse_sidlist()`, then calls `wb_lookupuseraliases_send(domain, num_sids, sids)`. The callback stores alias RID results. Recv composes full alias SIDs from the base domain SID and each returned RID with `sid_compose()`, appends textual SIDs to a newline-separated extra-data string, and sets `num_entries`.

## State And Persistence
No persistent local state. Alias lookup reads cache/domain state in lower layers.

## Dependencies And Integration Points
Uses SID parsing, domain lookup by SID, `wb_lookupuseraliases`, and response extra-data string conventions.

## Risks And Test Signals
Risks include malformed or non-null-terminated extra SID lists, unknown base domain SIDs, memory growth while appending large alias lists, and base-SID/RID composition assumptions. Test invalid SIDs, empty SID lists, no aliases, many aliases, trusted-domain aliases, and extra data lacking a final NUL.
