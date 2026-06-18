# sources/user-network-fs/samba/source3/auth/auth_util.c

## Purpose
This large utility file constructs user-supplied auth structures, creates local security/session tokens, builds and caches guest/anonymous/system session info, maps domain logon data to local Unix accounts, and provides guest mapping and session-key helpers.

## Important APIs, Types, and Functions
Input constructors include `make_user_info_map`, `make_user_info_netlogon_network`, `make_user_info_netlogon_interactive`, `make_user_info_for_reply`, `make_user_info_for_reply_enc`, and `make_user_info_guest`. Token/session functions include `create_local_token`, `auth3_user_info_dc_add_hints`, internal `auth3_session_info_create`, `make_session_info_from_username`, `init_guest_session_info`, `reinit_guest_session_info`, `init_system_session_info`, `make_server_info_guest`, `make_session_info_guest`, `make_server_info_anonymous`, `make_session_info_anonymous`, `make_session_info_system`, and `get_session_info_system`. Account mapping helpers include `_smb_create_user`, `check_account`, `smb_getpwnam`, `make_server_info_info3`, `make_server_info_wbcAuthUserInfo`, `is_trusted_domain`, `do_map_to_guest_server_info`, and `session_extract_session_key`.

## Control Flow
User-info constructors normalize or map SMB names, package LM/NT responses or plaintext, reject raw NTLMv2 when disabled, and set flags/logon parameters. `create_local_token` verifies the domain is allowed, reuses cached session info when present, otherwise builds Unix and NT tokens from server info, resolves SIDs to gids, adds Unix user/group SIDs, logs the token, and assigns a unique session GUID. `auth3_session_info_create` performs similar construction from source4 `auth_user_info_dc`, honoring S-1-5-88 Unix hint SIDs for uid/gid/name/translation behavior. Server-info conversion maps domain/user names to passwd records, can fall back from SID to UID, applies `min domain uid`, and handles `map to guest`.

## State and Persistence
Static cached pointers `guest_info`, `anonymous_info`, `guest_server_info`, and `system_info` persist for the process. External state can be changed by `_smb_create_user` running the configured add-user script and by winbind/passdb lookups. Token creation reads idmap, passwd, group, and configuration state but stores resulting tokens in talloc-owned session structures.

## Dependencies and Integration Points
The file integrates with passdb, winbind, id mapping, Unix passwd/group APIs, loadparm substitutions, token utilities, Netlogon SamInfo structures, PAM/account policy indirectly, and source4 auth info. It is used by nearly every backend to move from credentials to usable server/session identity.

## Risks and Test Signals
Risks include executing administrator-configured scripts with substituted usernames, domain firewall bypass mistakes, stale cached guest/system info after configuration changes, SID-to-UID mapping failures, ownership mistakes around cached session info, and guest mapping policy surprises. Test signals include guest/anonymous/system initialization, `map to guest` modes, domain UID minimum enforcement, winbind default-domain behavior, S-1-5-88 hint handling, SID/gid round-trips, token debug output, and session-key extraction for 16-byte and full-key use.
