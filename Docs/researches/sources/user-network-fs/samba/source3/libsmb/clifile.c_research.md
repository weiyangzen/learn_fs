# sources/user-network-fs/samba/source3/libsmb/clifile.c

## Purpose

`clifile.c` is the main source3 libsmb client file-operation layer. It exposes asynchronous `*_send`/`*_recv` APIs and synchronous wrappers for path info, file info, POSIX extensions, create/open/close, rename/hardlink/delete, directory operations, locks, attributes, disk size, extended attributes, change notify, query info, flush, shadow copy enumeration, and generic fsctl/ioctl operations. It hides most SMB1 versus SMB2 dispatch differences behind `struct cli_state`.

## Important APIs, Types, and Functional Areas

- Set/query info primitives: `cli_setpathinfo_send/recv`, `cli_setfileinfo_send/recv`, `cli_qpathinfo_send/recv`, `cli_qfileinfo_send/recv`.
- POSIX/UNIX extension operations: symlink/readlink/hardlink, getacl/setacl, stat, chmod/fchmod/chown, POSIX mknod/open/mkdir/unlink/rmdir, and POSIX byte-range locks.
- Rename/link/delete: `cli_rename`, `cli_ntrename`, `cli_hardlink`, `cli_unlink`, `cli_mkdir`, `cli_rmdir`, `cli_nt_delete_on_close`.
- Open/create/close: `cli_ntcreate`, SMB1 `cli_ntcreate1`, `cli_nttrans_create`, `cli_openx`, `cli_open`, `cli_close`, and `cli_ftruncate`.
- Locking: `cli_lockingx`, `cli_locktype`, `cli_lock32`, `cli_unlock`, `cli_posix_lock`, and `cli_posix_unlock`.
- Metadata and space: `cli_getattrE`, `cli_getatr`, `cli_setattrE`, `cli_setatr`, `cli_chkpath`, `cli_dskattr`, and `cli_disk_size`.
- EAs and notifications: `cli_set_ea_path`, `cli_set_ea_fnum`, `cli_get_ea_list_path`, `cli_notify`.
- Server features: `cli_shadow_copy_data` and `cli_fsctl_send/recv`.

Every operation is backed by small state structs allocated under the request, for example `cli_ntcreate_state`, `cli_lockingx_state`, `cli_notify_state`, `cli_qfileinfo_state`, and many operation-specific buffers.

## Control Flow

The dominant pattern is `tevent_req_create()`, protocol/path preparation, lower-level SMB request submission, callback completion, and a `*_recv()` accessor that returns `NTSTATUS` plus moved output buffers. Synchronous wrappers allocate a stackframe, create a private tevent context, reject use when `smbXcli_conn_has_async_calls(cli->conn)` is true, poll the request, call the matching recv function, and free the stackframe.

Protocol dispatch is pervasive. SMB2 paths generally call `cli_smb2_*` helpers directly. SMB1 paths build command words and byte buffers manually (`cli_smb_send`, `cli_smb_req_create`, or `cli_trans_send`). Some operations have SMB1 fallback ladders: `cli_open()` maps POSIX-style open flags to NTCreate parameters, tries `cli_ntcreate()`, treats many unsupported statuses as a signal to fallback to `cli_openx()`, and closes broken directory handles that violate `FILE_NON_DIRECTORY_FILE`.

DFS and previous-version paths are handled at call sites. SMB1 path-based commands against DFS shares call `smb1_dfs_share_path()`. Rename and hardlink targets can call `cli_dfs_target_check()` to strip DFS prefixes where servers expect target-local names. `@GMT` previous-version paths set `FLAGS2_REPARSE_PATH` for non-UNIX info levels and relevant SMB1 commands.

Create/open flows parse server-returned create metadata into `struct smb_create_returns`. SMB2 hardlink opens the source file, sends `FSCC_FILE_LINK_INFORMATION`, then closes the file while preserving the set-info status. Notify sends long-running change-notify requests with timeout temporarily set to zero and supports cancellation by forwarding cancellation to the child request.

## State and Persistence Behavior

The module does not persist data outside the remote SMB server effects requested by the caller. Local state is request-scoped talloc memory: wire buffers, parsed output data, fnums, create-return structures, EA lists, notify changes, shadow-copy names, and fsctl output blobs. Synchronous wrappers use `talloc_stackframe()` for temporary lifetime management.

Remote state changes include creating/deleting/renaming files and directories, modifying ACLs/security descriptors, changing timestamps/attributes/EOF, setting delete-on-close, byte-range locks, flushing data, setting EAs, creating reparse points for special files, and subscribing to notify changes. Some helpers temporarily mutate client timeout (`cli_notify`, `cli_lockingx`) and restore it afterward; `cli_open()` may open then close a handle when detecting broken directory behavior.

## Dependencies and Integration Points

This file integrates with the rest of Samba's client stack: `async_smb`, trans2/nttrans helpers, DFS helpers from `clidfs.c`, SMB2 fnum helpers, security descriptor marshalling, POSIX mode/dev conversion helpers, EA structures, notify structures, reparse point marshalling, and the `smbXcli` protocol abstraction. It is a central dependency for higher-level tools such as smbclient/libsmbclient and for tests that exercise SMB file semantics.

## Risks and Edge Cases

- The file hand-builds many SMB1 wire buffers. Length fields, Unicode termination, and alignment are common risk points.
- Many sync wrappers duplicate the async-in-flight guard; missing that guard in new sync helpers can break request sequencing.
- SMB1/SMB2 behavior is intentionally not identical for every operation, especially POSIX extensions, chmod via NFS mode ACEs, reparse-point special files, and query-info level mappings.
- DFS path conversion must be correct per command. Some SMB1 commands require DFS names for source and destination; SMB2 rename/hardlink target paths may require stripped DFS prefixes.
- Network-response parsers validate minimum lengths for many paths, but EA blobs, notify buffers, shadow copy data, create responses, and referral-adjacent query buffers remain important fuzz targets.
- `cli_lockingx()` changes timeout for blocking locks and restores it only after normal completion; failures before restore are worth auditing.
- `cli_chmod_closed()` currently returns close errors before the saved chmod status, which can mask the chmod result if close fails.

## Test Signals

High-value tests include async and sync variants for each major operation, sync rejection with active async calls, SMB1 and SMB2 protocol dispatch, DFS share path behavior for every SMB1 path command, previous-version `@GMT` flagging, create/open fallback to OpenX, directory-handle correction in `cli_open()`, SMB2 hardlink close-after-error behavior, delete-on-close, set/get attr time-zone conversions, disk-size fallback from full-size-info to core dskattr, EA blob parsing with malformed lengths, POSIX stat 100-byte response validation, notify parsing and cancellation, shadow-copy count-only versus names mode, fsctl SMB1/SMB2 output ownership, and timeout restore around notify and locking.
