<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getmemberships.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getmemberships.c

## Purpose
This file implements varlink `GetMemberships`: enumerate all user/group membership pairs, list groups for one user, list members of one group, and check a specific user/group membership.

## Important APIs, Types, And Functions
Reply helpers are `membership_reply()` and `member_list_reply()`. Public handlers are `wb_vl_memberships_enumerate()`, `wb_vl_memberships_by_user()`, `wb_vl_memberships_by_group()`, and `wb_vl_membership_check()`. The implementation uses async winbind `SETGRENT`, `GETGRENT`, `ENDGRENT`, `GETGROUPS`, `GETGRGID`, and `GETGRNAM` calls.

## Control Flow
Enumeration requires group enumeration, group expansion, and the varlink `more` flag. It walks group chunks, skips groups without members, keeps one member-bearing group delayed so the final reply can omit `continues`, and emits one varlink record per member. The by-user path calls `GETGROUPS`, then resolves each returned gid through `GETGRGID` to emit group names. The by-group path gets the group record and emits each member. The check path gets the group and scans its comma-separated member list for the requested username.

## State And Persistence Behavior
All operational state is per call and talloc-scoped: fake client/request objects, copied usernames/groupnames, gid arrays, delayed group/member data, and a referenced call object. `vl_active` is cleared in destructors. No persistent winbind data is modified.

## Dependencies And Integration Points
It depends on varlink, winbind group expansion behavior, `lp_winbind_expand_groups()`, group enumeration support, and internal async NSS handlers. It is the membership side of the systemd userdb integration.

## Risks And Test Signals
This file is sensitive to compile and control-flow correctness. The checked-out source has suspicious constructs including an undefined-looking `struct memberships_enum_state` in the enumeration connection-closed callback and historical-looking duplicate declarations/error arguments in nearby code, so build coverage with `with_systemd_userdb` is essential. Behavioral risks include `strtok_r` mutating member buffers, `GETGROUPS` gid ordering being reversed while emitted, no-record behavior for groups with zero members, and exact `continues` handling. Tests should cover all four modes, disabled expansion, missing `more`, users with one and many groups, empty groups, and positive/negative membership checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink_getmemberships.c -->
