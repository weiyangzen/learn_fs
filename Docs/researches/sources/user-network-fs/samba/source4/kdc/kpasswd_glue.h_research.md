## sources/user-network-fs/samba/source4/kdc/kpasswd_glue.h

Purpose: declaration of the SAMDB password-change helper used by kpasswd and MIT KDB password-change paths.

Important API: `samdb_kpasswd_change_password()` takes loadparm/event contexts, authenticated `session_info`, UTF-16 password blob, output password-policy reject reason/domain info/error string, and an `NTSTATUS *result` for the actual password operation.

Control flow and integration: callers treat a non-OK function return as infrastructure/access failure and a non-OK `result` as an authenticated password-change outcome to encode for the client.

State and persistence: no state in the header; persistence happens in the C implementation via SAMDB.

Dependencies: requires Samba auth, loadparm, tevent, `DATA_BLOB`, SAMR password-policy types, and NTSTATUS definitions from includers.

Risks: the split between return status and result status is subtle and should be documented in callers. Password blob encoding is expected to be UTF-16 before invocation.

Test signals: compile all callers and confirm policy reject paths preserve both `reject_reason` and `dominfo`.
