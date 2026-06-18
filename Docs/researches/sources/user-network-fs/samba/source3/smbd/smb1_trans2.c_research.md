# sources/user-network-fs/samba/source3/smbd/smb1_trans2.c

## Purpose

`smb1_trans2.c` implements Samba's SMB1 Transaction2 request path. It parses primary `SMBtrans2` and secondary `SMBtranss2` packets, accumulates fragmented parameter/data payloads in `struct trans_state`, dispatches Transaction2 subcommands, and serializes one or more Transaction2 responses. The file is a major compatibility surface for SMB1 clients: open, directory search, filesystem information, file/path information, POSIX extensions, DFS referrals, OS/2 printing ioctl support, and legacy find-notify stubs are all handled here.

## Important APIs, Types, and Functions

- `reply_trans2(struct smb_request *req)`: entry point for primary SMB1 trans2 packets. It validates word count and offsets, enforces IPC$ call restrictions, allocates `trans_state`, copies initial params/data, either dispatches immediately or queues the partial transaction on `conn->pending_trans`.
- `reply_transs2(struct smb_request *req)`: entry point for secondary trans2 fragments. It finds a matching pending transaction by MID, bounds-checks displacements, copies fragments, and dispatches when all params/data have arrived.
- `handle_trans2(...)`: central subcommand dispatcher for `TRANSACT2_OPEN`, `FINDFIRST`, `FINDNEXT`, `QFSINFO`, `SETFSINFO`, `QPATHINFO`, `QFILEINFO`, `SETPATHINFO`, `SETFILEINFO`, `MKDIR`, DFS referral, notify, and ioctl operations.
- `send_trans2_replies(...)`: response serializer and fragmenter. It obeys `max_data_bytes` and SMB1 `max_send`, calculates parameter/data offsets and displacements, applies SMB1 alignment padding, maps NTSTATUS to DOS error fields, and sends each packet with `smb1_srv_send`.
- Query handlers: `call_trans2qfsinfo`, `call_trans2qpathinfo`, `call_trans2qfileinfo`, `call_trans2qfilepathinfo`, `handle_trans2qfilepathinfo_result`, `call_trans2qpipeinfo`.
- Set handlers: `call_trans2setfsinfo`, `call_trans2setpathinfo`, `call_trans2setfileinfo`, `handle_trans2setfilepathinfo_result`.
- Directory enumeration: `call_trans2findfirst`, `call_trans2findnext`, `get_lanman2_dir_entry`, `smbd_dptr_name_equal`.
- POSIX extension helpers: `smb_set_posix_lock`, `smb_q_posix_lock`, `get_posix_fsp`, `smb_q_unix_basic`, `smb_q_unix_info2`, `smb_q_posix_acl`, `smb_q_posix_symlink`, `smb_posix_open`, `smb_posix_mkdir`, `smb_posix_unlink`, `smb_set_file_unix_link`, `smb_set_file_unix_hlink`, `smb_unix_mknod`, `smb_set_file_unix_basic`, `smb_set_file_unix_info2`, `smb_set_posix_acl`.

## Control Flow

Incoming primary requests enter `reply_trans2`. The function reads SMB parameter/data counts and offsets from `req->vwv`, validates them with `smb_buffer_oob`, copies payload bytes into heap buffers, and records transaction metadata such as return limits, setup count, call id, `mid`, `vuid`, and flags. Complete requests call `handle_trans2` immediately. Incomplete requests are linked into `conn->pending_trans` and get an interim empty response while later `reply_transs2` calls fill the missing ranges.

`reply_transs2` is the fragment continuation path. It rewrites the command code to `SMBtrans2` for Windows compatibility, finds the pending state by MID, clamps total counts if a client revises them downward, bounds-checks param/data displacements, updates received byte counters, and dispatches once the transaction is complete. Both primary and secondary paths free `state->data`, `state->param`, and the talloc state after dispatch or parameter failure.

`handle_trans2` enforces long-name flags for NT1-or-newer sessions and denies most calls when transport encryption is required but the request is not encrypted. It then dispatches to subcommand-specific handlers wrapped in profiling macros. Most handlers follow the same pattern: validate fixed parameter size, parse request-specific values with little-endian helpers, convert SMB1 strings into Samba path structures, call common smbd/VFS helpers, reallocate output parameter/data buffers, and finish through `send_trans2_replies`.

Directory enumeration opens a directory FSP, creates a `dptr` search handle, saves wildcard and attribute state in that handle, fills entries through `smbd_dirptr_lanman2_entry`, and optionally closes the search handle based on find flags. `FINDNEXT` retrieves the saved dptr, optionally rewinds to a resume name, continues filling entries, and closes the handle when requested or at end of search.

Path and file information handlers split into native/common info levels and SMB1 UNIX extension levels. Common levels delegate to `smbd_do_qfilepathinfo` and `smbd_do_setfilepathinfo`; UNIX levels use local helpers to marshal POSIX wire formats or perform POSIX open, unlink, ACL, symlink, hardlink, mode, owner, group, size, time, and flag changes.

## State and Persistence Behavior

The file persists partial transaction state in `conn->pending_trans` until all fragments arrive or an error removes the state. Directory searches persist through `dptr` handles attached to directory `files_struct` instances, including wildcard, attr mask, last name sent, case sensitivity, and backup-privilege state. `SETFSINFO` persists client UNIX capability negotiation in `xconn->smb1.unix_info` and may switch name mangling to POSIX path mode. SMB1 POSIX lock requests persist byte-range lock state through Samba's locking subsystem. File/path setters update persistent filesystem state through the VFS: metadata, ACLs, link creation, unlink/delete-on-close, truncation, mknod, quota data, and timestamps. Transport encryption setup can transition the connection into encrypted mode.

## Dependencies and Integration Points

This file integrates with the core smbd request stack (`struct smb_request`, `connection_struct`, `smbXsrv_connection`), SMB1 packet helpers, Transaction2 constants from `trans2.h`, VFS create/stat/link/ACL APIs, common query/set helpers in smbd, directory pointer code from `source3/smbd/dir.h`, DFS referral setup, quota and print helpers, byte-range locking, share mode locks, server encryption setup, POSIX create contexts from SMB2 POSIX helpers, and Samba configuration checks such as `lp_smb1_unix_extensions`, `lp_ea_support`, `lp_blocking_locks`, `lp_follow_symlinks`, `lp_dont_descend`, and encryption policy. `file_fsp` and `filename_convert_smb1_search_path` come from `smb1_utils.c`.

## Risks and Edge Cases

The highest-risk areas are packet sizing, offset/displacement validation, and response fragmentation. `send_trans2_replies` must keep SMB offsets, padding, `max_send`, and `max_data_bytes` consistent or clients can misparse responses. The request assembly paths guard against out-of-bounds copies, but they depend on correct `smb_buffer_oob` use for every fragment. Directory enumeration deliberately overallocates by `DIR_ENTRY_SAFETY_MARGIN`; regressions around max-data handling can leak uninitialized bytes or truncate entries incorrectly. POSIX extensions are sensitive because they map SMB1 wire requests to real UNIX metadata changes and special file creation. Symlink/hardlink handling, snapshot token stripping, backup privilege escalation, and root transitions must preserve share boundaries and restore privileges. Async POSIX lock handling returns `NT_STATUS_EVENT_PENDING`; callers must not send a second response while the lock callback owns completion.

## Test Signals

Useful test coverage includes SMB1 trans2 fragmentation with primary and secondary packets, invalid offset/displacement/count fuzzing, `raw.search` and OS/2 resume-name behavior, findfirst/findnext close flag combinations, EA list validation, encrypted-share denial/allowance for `QFSINFO` and `SETFSINFO`, IPC$ allowed-call matrix, DFS referral on IPC$, SMB1 UNIX extension negotiation, POSIX open/mkdir/unlink/link/ACL/lock query and set operations, delete-pending handling for streams, sharing-violation deferral, quota setting, OS/2 print ioctl job id handling, and response truncation with `STATUS_BUFFER_OVERFLOW`.
