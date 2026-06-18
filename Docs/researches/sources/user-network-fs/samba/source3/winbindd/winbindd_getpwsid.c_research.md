# sources/user-network-fs/samba/source3/winbindd/winbindd_getpwsid.c

## Purpose
Implements async `WINBINDD_GETPWSID`, resolving a textual SID directly to a passwd record.

## Important APIs, Types, And Control Flow
`winbindd_getpwsid_send()` null-terminates `request->data.sid`, parses it with `string_to_sid()`, rejects invalid strings with `NT_STATUS_INVALID_PARAMETER`, and starts `wb_getpwsid_send()`. `winbindd_getpwsid_done()` receives the helper result. `winbindd_getpwsid_recv()` copies the passwd record to `response->data.pw`.

## State And Persistence
No persistent state. SID-to-passwd mapping and any NSS/idmap cache effects are handled in `wb_getpwsid`.

## Dependencies And Integration Points
Uses `security.h` SID parsing, winbind async passwd helper, and standard tevent request response conventions.

## Risks And Test Signals
Test invalid SID syntax, unknown SIDs, user vs non-user SID behavior, SID mapped as ID_TYPE_BOTH, and long generated passwd names/gecos/dirs. The main wrapper risk is returning useful diagnostics without leaking malformed input into downstream helpers.
