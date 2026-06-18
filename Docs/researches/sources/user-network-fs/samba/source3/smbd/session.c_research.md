# sources/user-network-fs/samba/source3/smbd/session.c

## Purpose

`session.c` handles smbd session registration with PAM and utmp and provides APIs to list or filter recorded SMB sessions. It bridges SMBX session lifecycle with system login/session accounting, while avoiding expensive PAM work for guest or lower-than-user security contexts.

## Important APIs, Types, And Functions

- `session_claim()` is called when a session is created and claims PAM/utmp state for non-guest users.
- `session_yield()` is called when a session is destroyed and releases utmp/PAM state.
- `list_sessions()` returns active sessionid records.
- `find_sessions()` returns active sessionid records matching username and remote machine filters.
- `gather_sessioninfo()` is the traversal callback that filters sessionid DB records and drops records whose process no longer exists.
- `struct session_list` carries traversal memory context, count, filters, and the accumulated `struct sessionid` array.

## Control Flow

On claim, the function fetches `auth_session_info` from `session->global`, skips registration unless `security_session_user_level()` is at least `SECURITY_USER`, formats an ID string as `smb/<session_global_id>`, asserts that source3 has a `unix_token`, obtains the Unix username and first channel remote name, calls `smb_pam_claim_session()`, and optionally writes utmp if `lp_utmp()` is enabled. On yield, it formats the same ID, asserts the Unix token, obtains username/hostname, removes utmp if configured, and closes the PAM session.

Listing and finding sessions traverse the sessionid database through `sessionid_traverse_read()`. The callback applies optional exact user and machine filters, skips dead PIDs using `process_exists()`, reallocates the output array under the caller's context, copies the record, and increments the count.

## State And Persistence Behavior

This file writes to external system/session accounting through PAM and utmp helpers. It reads the Samba sessionid database for list/find operations but does not itself create sessionid records in this file. Returned arrays are talloc-owned by the caller's context. PAM/utmp identifiers derive from `session_global_id`, making claim/yield pairing dependent on stable SMBX session global state.

## Dependencies And Integration Points

It depends on `smbXsrv_session`, `auth_session_info`, security session-level helpers, PAM wrappers, utmp wrappers, sessionid DB traversal, process-existence checks, loadparm `utmp`, and tsocket/security headers. It integrates with session setup/logoff and administrative session enumeration features.

## Risks

Guest-session skip is intentional for performance, but any incorrect security level could skip accounting. The code assumes `channels[0].remote_name` is valid. `SMB_ASSERT(session_info->unix_token)` makes missing Unix-token setup a hard failure in source3. Listing silently filters dead PIDs, so stale DB records may not be visible to callers. `talloc_realloc()` failure resets count and aborts traversal with `-1`; callers receive zero sessions after the error path logs.

## Test Signals

Tests should cover non-guest claim/yield invoking PAM and utmp with matching IDs, guest skip behavior, disabled utmp behavior, PAM claim rejection returning false, list/find filtering by user and machine, dead-PID filtering, traversal failure handling, and missing Unix-token assertions in developer/selftest builds.
