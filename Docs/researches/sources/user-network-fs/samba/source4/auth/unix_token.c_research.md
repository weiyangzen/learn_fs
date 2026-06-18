# sources/user-network-fs/samba/source4/auth/unix_token.c

Purpose: converts Windows security-token/session data into UNIX uid/gid/group identity data for filesystem/process access.

Important APIs: `security_token_to_unix_token()` maps token SIDs to UNIX ids. `fill_unix_info()` creates `auth_user_info_unix` names. `auth_session_info_fill_unix()` fills both UNIX token and info from a session. `auth_session_info_set_unix()` manually sets uid/gid without winbind lookup.

Control flow: SYSTEM tokens get a zeroed `security_unix_token`, implying uid/gid 0. Normal tokens must contain primary user and group SIDs. The code builds an `id_map` array, calls `wbc_sids_to_xids()`, derives uid from primary user SID, gid from primary group SID, and group list from all GID-capable SIDs. Name filling combines domain, winbind separator, and account name, then sanitizes the original username.

State/dependencies/integration: no persistent writes. Results are talloc-owned under the session or caller context. Depends on security token helpers, winbind client SID-to-XID mapping, and loadparm's winbind separator. Used when Samba needs POSIX credentials after authentication.

Risks/test signals: access is denied for tokens lacking primary SID slots; unmappable primary or group SIDs fail with `NT_STATUS_INVALID_SID`. Manual uid/gid setting must only be used by trusted callers. Coverage is indirect.
