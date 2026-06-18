## sources/user-network-fs/samba/source4/kdc/kpasswd_glue.c

Purpose: SAMDB glue for self-service kpasswd password changes. It converts authenticated Kerberos session information into a user-privileged SAMDB operation and returns Samba password-policy details to the kpasswd layer.

Important APIs and functions: `samdb_kpasswd_change_password()` opens SAMDB with `samdb_connect()` using the caller's `auth_session_info`, logs the account and SID, and invokes `samdb_set_password_sid()` for the primary user SID with `DSDB_PASSWORD_CHECKED_AND_CORRECT`.

Control flow: connection failure returns `NT_STATUS_ACCESS_DENIED` and an error string. `samdb_set_password_sid()` status is copied into `*result`; no-such-user and other failures populate human-readable error strings, but the function itself returns `NT_STATUS_OK` after the SAMDB operation so the caller can encode the policy outcome in the kpasswd reply.

State and persistence: the durable change is the password write through SAMDB. Reject reason and domain password policy info are returned via output pointers for reply formatting. The SAMDB connection is talloc-scoped to `mem_ctx`.

Dependencies and integration: used by MIT/Heimdal kpasswd service handlers and by `mit_samba_kpasswd_change_password()` for MIT KDB password changes. Depends on DSDB/SAMDB, session tokens, primary SID layout, and SAM password policy structures.

Risks: relies on `PRIMARY_USER_SID_INDEX` being valid in the session token. Returning `NT_STATUS_OK` even when the password result failed is intentional but can be misread by callers; they must inspect `*result`.

Test signals: no SAMDB connection, no such user, policy rejects, successful password change, and verification that the write runs as the authenticated user rather than system.
