<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_winbind.c -->
# sources/user-network-fs/samba/source4/auth/ntlm/auth_winbind.c

Purpose: implements the `winbind` auth4 backend, forwarding authentication to the winbind server over IRPC/Netlogon SamLogon.

Important APIs: `winbind_want_check()` accepts nonempty mapped accounts. `winbind_check_password_send()` initializes an imessaging client, binds to `winbind_server`, converts supplied credentials to either Netlogon interactive password info or network challenge-response info, fills `winbind_SamLogon`, and sends `dcerpc_winbind_SamLogon_r_send()`. `winbind_check_password_done()` converts Netlogon validation into `auth_user_info_dc`, performs local success accounting if the returned domain is local, expands local group memberships with `authsam_update_user_info_dc()`, and completes. `auth4_winbind_init()` registers the backend.

Control flow: netlogon auth contexts set `WB_SAMLOGON_FOR_NETLOGON`. Interactive logons use hash conversion and logon level 1; network logons use response conversion, current challenge, and logon level 2. The binding timeout is set to 120 seconds to allow trusted-domain and RODC scenarios. `NT_STATUS_IO_TIMEOUT` maps to `NT_STATUS_NO_LOGON_SERVERS`; non-authoritative winbind failures propagate that flag to the auth chain.

State and persistence: per-request state stores request parameters, user info, output user info, and authoritative flag. It may update local SAM logon accounting for local-domain accounts and group expansion can mutate returned token information.

Dependencies and integration: depends on winbind generated RPC, imessaging/IRPC, libwbclient, auth SAM reply conversion, local SAM search/accounting, and auth credential conversion utilities. It handles domain-member and trusted-domain authentication paths in the default method chain.

Risks and test signals: winbind server absence must produce `NO_LOGON_SERVERS`, not crashes. Tests should cover interactive vs network inputs, timeout mapping, non-authoritative fallback, local-domain accounting reset, group expansion on RODC/trusted users, netlogon internal flag, and correct use of client domain/account rather than mapped fields in Netlogon identity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/auth/ntlm/auth_winbind.c -->
