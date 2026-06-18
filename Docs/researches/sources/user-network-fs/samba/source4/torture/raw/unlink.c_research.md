# sources/user-network-fs/samba/source4/torture/raw/unlink.c

## Purpose
`unlink.c` is the raw SMB unlink/delete torture suite. It validates plain unlink status codes, hidden-file attribute matching, directory rejection, bad path syntax, delete-on-close behavior for files and directories, non-empty directory semantics, and unlink deferral around oplock breaks.

## Important APIs, types, and functions
The suite entry point is `torture_raw_unlink()`. Test cases are `test_unlink()`, `test_delete_on_close()`, and `test_unlink_defer()`. The oplock callback is `oplock_handler_ack_to_none()`, with `struct unlink_defer_cli_state` carrying context and client state. The file uses `union smb_unlink`, `union smb_open`, `union smb_setfileinfo`, `struct smb_rmdir`, `smb_raw_unlink()`, `smb_raw_rmdir()`, `smb_raw_open()`, `smb_raw_setfileinfo()`, `smb_raw_setfileinfo_send()`, `smbcli_oplock_handler()`, and `smbcli_oplock_ack()`.

## Control flow
The plain unlink test creates `\testunlink`, verifies missing files return `OBJECT_NAME_NOT_FOUND`, deletes a normal file, requires hidden-file attribute matching, rejects directories through unlink even with directory attributes, and checks several `..` path forms for syntax or directory errors. The delete-on-close test sets `RAW_SFILEINFO_DISPOSITION_INFO` on file and directory handles with both false and true values, closes handles, then verifies whether subsequent unlink/rmdir sees the object. It also checks non-empty directory delete-on-close behavior, skipping a known Samba3 deficiency, and exercises delete-on-close create options on directories with child files. The deferred unlink test installs an oplock handler, opens a file with a batch oplock on one client, then unlinks from a second client so the server must break the oplock; the handler marks delete-on-close and acknowledges to none.

## State and persistence behavior
All persistent objects are temporary under `\testunlink`. The tests create files, directories, and inside-directory files, mutate disposition flags, and rely on handle close to commit deletion. The oplock deferral path temporarily stores callback state in `unlink_defer_cli_state` and issues an async setfileinfo request from inside the oplock handler.

## Dependencies and integration points
This file integrates raw unlink/rmdir, raw open, disposition setfileinfo, oplock break dispatch, and SMB session cleanup. It depends on test helpers for complex file creation and directory handles, and uses the `samba3` setting for compatibility skips. It is relevant to share-mode, delete-on-close, open-file database, and oplock break implementations.

## Risks and edge cases
The oplock handler closes the file before acknowledging the break and starts an async setfileinfo without receiving it, so it specifically probes ordering-sensitive server behavior. Some directory delete-on-close cases are expected to keep non-empty directories alive even after close. Path syntax expectations for `..` are protocol compatibility-sensitive. Cleanup uses `smbcli_deltree()`, which must handle partially deleted state.

## Test signals
Expected signals include exact hidden-file and directory NTSTATUS values, delete-on-close removing files/directories only when allowed, `DIRECTORY_NOT_EMPTY` for non-empty directory disposition attempts, and successful handling of an unlink that is deferred by an oplock break and races with delete-on-close.
