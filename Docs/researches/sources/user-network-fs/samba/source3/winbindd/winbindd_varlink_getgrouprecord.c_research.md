<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getgrouprecord.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getgrouprecord.c

## Purpose
This file implements varlink `GetGroupRecord` operations: enumerate groups, lookup by gid, lookup by name, and lookup by both name and gid with conflict detection.

## Important APIs, Types, And Functions
`group_record_reply()` converts a `winbindd_gr` plus comma-separated member data into a varlink record object. Public handlers are `wb_vl_group_enumerate()`, `wb_vl_group_by_gid()`, `wb_vl_group_by_name()`, and `wb_vl_group_by_name_and_gid()`. Each operation has a state struct, destructor that unrefs the varlink call and clears `vl_active`, async callbacks, and a connection-closed cleanup callback.

## Control Flow
Enumeration requires `lp_winbind_enum_groups()` and `VARLINK_CALL_MORE`, then runs `SETGRENT`, repeated `GETGRENT` chunks of 500, and `ENDGRENT`. It delays the final record from each chunk so the last reply can be sent without the `continues` flag. Single lookup paths synthesize `GETGRGID` or `GETGRNAM` requests and translate `NONE_MAPPED` to `NoRecordFound`. The name+gid path tries name first, falls back to gid if name is missing, and returns `ConflictingRecordFound` if the resolved record does not match both requested fields.

## State And Persistence Behavior
State is per varlink call: fake winbind request/client structures, a referenced `VarlinkCall`, last delayed group record, and copied member string where needed. It mutates `vl_active` and per-fake-client enumeration state but no persistent database.

## Dependencies And Integration Points
It depends on varlink object/array APIs, winbind getgr* async handlers, `winbindd_setgrent/endgrent`, Samba string wrappers, and `lp_winbind_enum_groups()`. It integrates with systemd userdb group record consumers.

## Risks And Test Signals
Risks include parsing member strings destructively with `strtok_r`, correct `continues` flag handling across chunk boundaries, gid/name integer range behavior, and fake-client state parity with real NSS clients. Tests should cover empty enumeration, disabled enumeration, multi-chunk enumeration, groups with and without members, lookup misses, and name/gid conflicts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getgrouprecord.c -->
