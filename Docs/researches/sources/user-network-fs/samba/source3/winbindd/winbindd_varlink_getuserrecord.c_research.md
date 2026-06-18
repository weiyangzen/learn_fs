<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getuserrecord.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getuserrecord.c

## Purpose
This file implements varlink `GetUserRecord` operations: enumerate users, lookup by uid, lookup by name, and lookup by both name and uid with conflict detection.

## Important APIs, Types, And Functions
`user_record_reply()` builds systemd userdb record objects from `struct winbindd_pw`. Public handlers are `wb_vl_user_enumerate()`, `wb_vl_user_by_uid()`, `wb_vl_user_by_name()`, and `wb_vl_user_by_name_and_uid()`. Each path uses a per-call state object, fake winbind request/client objects, callbacks, and connection-closed cleanup.

## Control Flow
Enumeration requires `lp_winbind_enum_users()` and `VARLINK_CALL_MORE`, runs `SETPWENT`, repeated `GETPWENT` chunks of 500, and `ENDPWENT`, delaying the last record so the final reply lacks `continues`. UID and name lookups synthesize `GETPWUID` or `GETPWNAM` requests and translate `NONE_MAPPED` to `NoRecordFound`. Name lookup overwrites the returned username with the requested string so systemd's multiplexer accepts UPN lookups. Name+uid first tries name, falls back to uid on miss, and returns `ConflictingRecordFound` if both fields do not match.

## State And Persistence Behavior
The file uses only per-call memory plus `vl_active`. It relies on normal winbind caches and NSS state below the async handlers but does not persist records itself.

## Dependencies And Integration Points
It depends on varlink, winbind getpw* async commands, `winbindd_setpwent/endpwent`, `lp_winbind_enum_users()`, and string wrappers. It integrates with systemd userdb clients through `winbindd_varlink.c`.

## Risks And Test Signals
Risks include chunk-boundary `continues` handling, fake-client parity, integer range conversion from varlink `int64_t` to uid fields, name rewriting for UPNs, and conflict semantics when name and uid identify different records. Tests should cover disabled enumeration, missing `more`, multi-chunk enumeration, uid/name misses, UPN lookups, and name+uid conflicts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getuserrecord.c -->
