<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/sessid.c -->
# sources/user-network-fs/samba/source4/torture/smb2/sessid.c

## Purpose
`sessid.c` verifies SMB2 server handling of requests sent with an invalid session id. It opens a file under a valid session, temporarily corrupts the SMB2 session id in the client, attempts a file information query, and expects the server to reject it with `NT_STATUS_USER_SESSION_DELETED`.

## Important APIs, Types, And Functions
The local helper `smb2cli_session_set_id()` preserves existing session flags while calling `smb2cli_session_set_id_and_flags()`. The exported test function is `run_sessidtest()`. It uses `struct smb2_tree`, `struct smb2_create`, `struct smb2_handle`, `union smb_fileinfo`, `smb2_util_unlink()`, `smb2_create()`, `smb2cli_session_current_id()`, `smb2_getinfo_file()`, and `smb2_util_close()`.

## Control Flow
The test removes `sessid.tst`, creates or overwrites it with read/write access and broad share access, and saves the returned handle. It records the current SMB2 session id from the tree's `smbXcli` session, sets the session id to `session_id + 1234`, then calls `smb2_getinfo_file()` for `RAW_FILEINFO_SMB2_ALL_INFORMATION` on the still-valid file handle.

If the query succeeds, the test fails immediately. Otherwise it asserts the exact status is `NT_STATUS_USER_SESSION_DELETED`. It restores the original session id before closing the handle and unlinking the file.

## State And Persistence
The only filesystem state is `sessid.tst`, which is removed before and after the test. The important mutable client state is the session id stored in the `smbXcli` session; it is deliberately corrupted for one request and restored before cleanup so the close can use the valid session again.

## Dependencies And Integration Points
This test is part of the SMB2 torture suite and uses the low-level SMB2 client session id setter from `smbXcli_base`. It validates server session lookup behavior independent of filename parsing or access checks because the handle is already valid but the session id is wrong.

## Risks
The helper stores the current session id in a `uint32_t` even though SMB2 session ids are 64-bit in the underlying API. If test environments ever use ids that do not fit in 32 bits, the saved/restored id could be truncated. The test also assumes adding 1234 creates a definitely invalid id, which is extremely likely but not formally impossible if ids are reused or truncated in unusual test harnesses.

## Test Signals
The expected signal is a failed `smb2_getinfo_file()` returning exactly `NT_STATUS_USER_SESSION_DELETED`, followed by successful restoration of the original session id, successful close, and cleanup unlink. Any success with the wrong id or a different error status is a server behavior difference worth investigating.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/torture/smb2/sessid.c -->
