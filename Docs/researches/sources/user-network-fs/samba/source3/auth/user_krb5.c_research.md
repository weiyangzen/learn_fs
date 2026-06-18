<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_krb5.c -->
# sources/user-network-fs/samba/source3/auth/user_krb5.c

## Purpose
Maps a Kerberos principal to a local Samba/UNIX user and creates a source3 session-info object when Kerberos authentication succeeds without enough PAC-derived session state. The file also provides `NOT_IMPLEMENTED` stubs when Samba is built without Kerberos.

## APIs, Types, and Functions
With `HAVE_KRB5`, `get_user_from_kerberos_info()` parses `user@REALM`, decides whether the realm is local or trusted, applies username mapping, resolves a UNIX account through `smb_getpwnam()`, performs PAM account checks, optionally maps bad UIDs to guest, and returns NT user/domain, UNIX username, passwd data, and mapping flags. `make_session_info_krb5()` builds `auth_serversupplied_info` as guest, passdb-backed (`make_server_info_sam()`), or artificial passwd-backed (`make_server_info_pw()`), fixes the logon domain when possible, tags `nss_token` if the username was mapped, and calls `create_local_token()`.

## Control Flow, State, and Persistence
Principal parsing rejects names without `@`. Local-realm principals use the workgroup domain and may retry lookup using the bare user after a failed `DOMAIN\user` lookup; foreign realms require `allow trusted domains` and use the realm as the NT domain. Mapping is applied before UNIX lookup. If no passwd entry exists and `map to guest = Bad Uid`, the guest account is looked up and `mapped_to_guest` is set. Session creation then chooses guest server-info, passdb server-info, or passwd-derived server-info and moves into local token creation. No durable state is written; returned strings and passwd wrappers live on the caller's talloc context or the provided passwd allocation lifetime.

## Dependencies and Integration
Depends on Kerberos build configuration, `auth.h`, generated PAC headers, winbind client headers, passdb, loadparm settings such as realm/workgroup/trusted domains/guest mapping, username mapping from `user_util.c`, PAM account restrictions, and token creation. It integrates Kerberos-authenticated SMB session setup with the same local token and passdb identity paths used by NTLM authentication.

## Risks and Test Signals
Risks include realm case/normalization mismatches, trusted-domain policy rejecting valid foreign principals, username map changes altering `DOMAIN\user` lookup behavior, PAM account checks denying otherwise authenticated Kerberos users, guest fallback hiding missing local accounts when configured, and artificial server-info needing explicit domain correction. Test signals include local realm with and without domain-qualified UNIX accounts, foreign realm allowed/denied, mapped usernames, guest mapping on bad UID, PAM restriction failures, passdb-present versus passdb-absent users, and no-Kerberos builds returning `NT_STATUS_NOT_IMPLEMENTED`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/auth/user_krb5.c -->
