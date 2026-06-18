# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwuid.c

## Purpose
Implements async `WINBINDD_GETPWUID`, resolving a Unix UID to a passwd record through idmap and SID lookup.

## Important APIs, Types, And Control Flow
`winbindd_getpwuid_send()` builds a single `struct unixid` with `ID_TYPE_UID` and calls `wb_xids2sids_send()`. `uid2sid_done()` receives a SID pointer, rejects null SID as `NT_STATUS_NO_SUCH_USER`, then calls `wb_getpwsid_send()` to populate `state->pw`. `winbindd_getpwuid_done()` validates the helper result. Recv copies the passwd record into the winbind response.

## State And Persistence
Only request-local state. Reads idmap and account data through helpers and caches outside this file.

## Dependencies And Integration Points
Uses `wb_xids2sids`, `wb_getpwsid`, `dom_sid` helpers, and winbind response structures.

## Risks And Test Signals
Test unmapped UIDs, null SID returns, ID_TYPE_BOTH mappings, idmap backend failures, user records with missing NSS attributes, and request union correctness for UID fields.
