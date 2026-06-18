# sources/user-network-fs/samba/source3/torture/test_smb2.c

## Purpose

`test_smb2.c` is a Samba source3 torture module that exercises SMB2 and SMB3 client/server behavior through the low-level `smb2cli_*` APIs and the higher-level `cli_*` wrappers. It is not a generic unit-test file; each exported `run_*` function is an integration-style torture entry point that creates real SMB sessions, tree connections, handles, files, directories, alternate data streams, DFS paths, and named pipe opens against the configured torture server/share.

The file validates protocol correctness around negotiation, session setup, reconnect, reauthentication, multichannel, tree/session invalidation, directory fsync permissions, truncation, path normalization, SACL and stream ACL handling, quota edge cases, delete-on-close semantics, DFS pathname parsing, and named pipe error behavior. Several tests encode Windows-compatible status expectations and Samba bug regressions.

## Important APIs, Types, and Functions

Primary state types:

- `struct cli_state`: Samba source3 client state, including `conn`, `timeout`, `smb2.session`, `smb2.tcon`, and share metadata.
- `struct smbXcli_session` and `struct smbXcli_tcon`: SMB2 session and tree-connect handles stored inside `cli_state`, sometimes deliberately replaced or forged to test invalid IDs.
- `struct tevent_context` and `struct tevent_req`: async request context for manual SMB2 session setup and pipe read tests.
- `DATA_BLOB`, `struct iovec`, and `struct auth_generic_state`: GENSEC/NTLMSSP security token exchange and session/channel key extraction.
- `struct security_descriptor`: DACL/SACL descriptors used for SACL and stream ACL tests.
- `SMB_NTQUOTA_STRUCT`: quota query result container.

Major Samba APIs exercised:

- Connection/session setup: `torture_init_connection`, `torture_close_connection`, `smbXcli_negprot`, `cli_session_setup_creds`, `cli_tree_connect`, `cli_tree_connect_creds`, `smb2cli_session_setup_send`, `smb2cli_session_setup_recv`, `smb2cli_session_set_session_key`, `smb2cli_session_create_channel`, `smb2cli_session_set_channel_key`.
- SMB2 file operations: `smb2cli_create`, `smb2cli_write`, `smb2cli_read`, `smb2cli_flush`, `smb2cli_close`, `smb2cli_query_directory`, `smb2cli_query_info`, `smb2cli_set_info`, `smb2cli_tdis`, `smb2cli_logoff`.
- Source3 convenience wrappers over SMB2: `cli_ntcreate`, `cli_smb2_create_fnum`, `cli_smb2_close_fnum`, `cli_writeall`, `cli_ftruncate`, `cli_qfileinfo_basic`, `cli_set_security_descriptor`, `cli_query_security_descriptor`, `cli_smb2_get_user_quota`, `cli_nt_delete_on_close`, `cli_list`, `cli_mkdir`, `cli_rmdir`, `cli_unlink`, `cli_close`.
- Security helpers: `auth_generic_client_prepare`, `auth_generic_set_creds`, `auth_generic_client_start`, `gensec_update`, `gensec_want_feature`, `gensec_session_key`, `security_descriptor_sacl_create`.
- DFS/path helpers: `smbXcli_conn_dfs_supported`, `smbXcli_tcon_is_dfs_share`, `smbXcli_conn_remote_name`, `smb2cli_tcon_set_values`, `smb2cli_tcon_current_id`, `smb2cli_tcon_flags`, `smb2cli_tcon_capabilities`, `push_ucs2_talloc`, `PULL_LE_U64`, `PUSH_LE_U8`, `PUSH_LE_U32`.

Exported torture entry points include basic negotiation/IO (`run_smb2_basic`, `run_smb2_negprot`, `run_smb2_anonymous`), session lifecycle tests (`run_smb2_session_reconnect`, `run_smb2_tcon_dependence`, `run_smb2_multi_channel`, `run_smb2_session_reauth`), filesystem metadata tests (`run_smb2_ftruncate`, `run_smb2_dir_fsync`, `run_smb2_path_slash`, `run_smb2_sacl`, `run_smb2_quota1`, `run_smb2_stream_acl`, `run_list_dir_async_test`), delete-on-close tests, DFS tests, and named pipe tests.

## Control Flow

Most tests follow the same integration-test skeleton: initialize a client connection, negotiate an SMB2 or SMB3 dialect range, authenticate with `torture_creds`, tree-connect to `share` or `IPC$`, perform protocol operations, compare exact `NTSTATUS` values, clean up created remote objects, and return `true` only on all expected outcomes. Error reporting is direct `printf`/`d_printf` with `nt_errstr(status)`.

The session reconnect, multichannel, and reauth tests are the most stateful. They manually drive NTLMSSP/GENSEC token exchange with `smb2cli_session_setup_send/recv`, poll `tevent_req` objects synchronously, then install session or channel keys from `gensec_session_key`. These flows intentionally issue operations in intermediate states to assert expected server rejection, such as `NT_STATUS_USER_SESSION_DELETED`, `NT_STATUS_INVALID_HANDLE`, `NT_STATUS_FILE_CLOSED`, `NT_STATUS_NETWORK_NAME_DELETED`, or `NT_STATUS_ACCESS_DENIED`.

The DFS tests use low-level SMB2 APIs instead of `cli_*` wrappers so they test server pathname behavior rather than client-side path normalization. They first establish whether the server and share advertise DFS, derive a canonical `server\share` root name, query file IDs/inodes using `FSCC_FILE_ALL_INFORMATION`, and compare multiple syntactic paths against the same root inode. Rename and hardlink tests construct raw SMB2 set-info buffers and intentionally distinguish full DFS destination paths from relative names.

Helper callbacks and utilities include `list_fn` for directory match detection, `check_empty_fn` for delete-veto directory emptiness checks, `check_size` for truncation verification, `get_smb2_inode` and `smb2_inode_matches` for DFS inode comparisons, and `smb2_dfs_delete`/`smb2_dfs_rename`/`smb2_dfs_hlink` for raw DFS cleanup and set-info operations.

## State and Persistence Behavior

The tests create remote files/directories such as `smb2-basic.txt`, `session-reconnect.txt`, `multi-channel.txt`, `session-reauth.txt`, `smb2_ftruncate.txt`, `fsync_test_dir`, `smb2_dir_slash`, `smb2_file_slash`, `sacl_test_file`, `stream_acl_test_file`, `ASYNC_DIR`, `DEL_ON_CLOSE_DIR`, `file`, DFS test files, and stream names like `stream_acl_test_file:streamname`. Most are opened with `FILE_DELETE_ON_CLOSE`, explicitly unlinked/rmdir'd, or deleted through `smb2_dfs_delete` at test exit.

Session and tree state is deliberately mutated. Examples include saving and replacing `cli->smb2.tcon` to forge a TID, recreating `cli->smb2.session` with a stale UID, changing `cli_state_client_guid` to enable multichannel setup, and changing `smb2cli_tcon_set_values` capabilities to force or clear `SMB2_SHARE_CAP_DFS`. These mutations are central to the tests and create risk if cleanup paths do not restore handles before subsequent calls.

Memory is managed mostly with Samba's talloc hierarchy (`talloc_tos`, `talloc_asprintf`, `data_blob_talloc`, `TALLOC_FREE`). Handles are closed explicitly. Some early-return paths do not close every successfully opened object, but most tests either use delete-on-close semantics or cleanup labels to remove remote state.

## Dependencies and Integration Points

This file depends on the Samba source3 torture harness and runtime globals declared externally: `host`, `workgroup`, `share`, `password`, `username`, `myname`, and `torture_creds`. It integrates with SMB client libraries from `client.h`, `libsmb/proto.h`, `libsmb/clirap.h`, `libsmb/cli_smb2_fnum.h`, SMBX base transport/session code, GENSEC authentication, credentials, NDR/security descriptor support, and trans2/FSCC constants.

The tests require a live SMB server configured for the relevant scenario. Some entry points need specific share/server properties: SMB2/SMB3 dialect support, DFS-enabled or non-DFS shares, `SeSecurityPrivilege` for SACL testing, alternate data streams and ACL persistence for stream ACL testing, `smbd async dosmode = yes` for async DOS attribute listing, `hide unwritable` and `delete veto files` combinations for delete-on-close tests, and an accessible `IPC$` SAMR named pipe for pipe tests.

Outer Samba test scripts provide additional validation for some cases. For example, `run_smb2_pipe_read_async_disconnect` only confirms the client-side setup/disconnect path; the containing no-crash script checks that the server did not crash.

## Risks and Edge Cases

- The tests encode exact Windows-compatible statuses, but some comments note version differences such as Windows 2008 versus Windows 2022 DFS empty-server behavior and Win8 pre-release SMB2.22 reauth quirks.
- Several tests intentionally tamper with client state (`cli->smb2.tcon`, session IDs, DFS capability bits). Future client library changes that assume these fields are immutable could break the tests or hide server regressions.
- Cleanup is best-effort on many failure paths. Failed runs can leave files or directories on the target share, though most tests pre-clean their known names.
- SACL, DFS, delete-veto, async DOS mode, stream ACL, and named pipe tests are environment-sensitive and can fail because the test server is not configured for the scenario rather than because protocol code regressed.
- The DFS helpers extract inode/file IDs from a fixed offset in `FSCC_FILE_ALL_INFORMATION`; layout changes or server-specific response differences could affect comparisons.
- `run_smb2_multi_channel` temporarily changes the global `cli_state_client_guid`; it restores after three connections are initialized, but early failures before restoration would be risky if future edits move the restore point.

## Test Signals

Strong pass signals include exact `NT_STATUS_OK` for successful creates/reads/writes/flushes/closes, exact negative statuses for invalid handles or invalid paths, byte-for-byte readback of `"Hello, world\n"`, file-size checks after truncation, inode equality for DFS aliases, DACL bit changes on streams, and expected delete-on-close results. The tests print the failing API and observed `NTSTATUS`, making failures actionable in torture logs.

Regression signals are especially tied to historic Samba bugs documented in comments: async DOS attribute listing, delete-on-close race/nonwrite behavior, DFS leading backslash parsing, and async pipe read disconnect no-crash behavior.
