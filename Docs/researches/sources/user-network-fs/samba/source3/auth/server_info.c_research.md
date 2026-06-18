# sources/user-network-fs/samba/source3/auth/server_info.c

## Purpose
This file converts between Samba's internal `auth_serversupplied_info`, Netlogon validation structures, PAC-derived information, passdb `samu` records, and Unix passwd records. It is the structural bridge from authentication results to domain-style SamInfo data.

## Important APIs, Types, and Functions
Public functions include `make_server_info`, `serverinfo_to_SamInfo2`, `serverinfo_to_SamInfo3`, `serverinfo_to_SamInfo6`, `create_info3_from_pac_logon_info`, `create_info6_from_pac`, `samu_to_SamInfo3`, and `passwd_to_SamInfo3`. Internal helpers include `append_netr_SidAttr`, `group_sids_to_info3`, `merge_resource_sids`, and `SamInfo3_handle_sids`.

## Control Flow
`make_server_info` allocates a zeroed server-info object and initializes UID/GID to `-1` to avoid accidental root use. Serverinfo-to-SamInfo conversions copy info3 and overlay session keys. PAC conversion copies logon info and merges resource-group SIDs into extra SIDs. `samu_to_SamInfo3` extracts SIDs, times, names, account flags, and group memberships from passdb. `passwd_to_SamInfo3` resolves a Unix username to a SID, determines primary group via winbind or gid mapping, normalizes unsuitable Unix/builtin/well-known group SIDs to Domain Users, and builds SamInfo3.

## State and Persistence
No persistent state is stored. The file reads passdb domain capabilities, passdb account data, winbind user SID lists, Unix passwd/gid data, and PAC contents, then creates talloc-owned output structures.

## Dependencies and Integration Points
Dependencies include Netlogon NDR types, security SID utilities, winbind client helpers, passdb, Unix SID conversion, and PAC structures. It is used by SAM, Unix, winbind, Kerberos/PAC, and server-info helper paths throughout the auth subsystem.

## Risks and Test Signals
Risks include invalid SID/domain RID handling, loss of extra/resource SIDs, incorrect primary group normalization, missing ADS passdb support for SamInfo6, session-key truncation/copy mistakes, and `passwd_to_SamInfo3` paths that differ when winbind is unavailable. Tests should cover PAC resource groups, SamInfo2/3/6 conversion, Unix user and group SID special cases, passdb group memberships, winbind/no-winbind passwd conversion, and UID/GID root-safety initialization.
