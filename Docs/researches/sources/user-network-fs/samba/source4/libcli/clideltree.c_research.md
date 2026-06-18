# sources/user-network-fs/samba/source4/libcli/clideltree.c

## Purpose

`clideltree.c` implements recursive deletion of a remote SMB path using the `smbcli_*` convenience APIs. It deletes files, descends into directories, clears read-only attributes when needed, and returns a count of deleted entries or `-1` on failure.

## Important APIs, Types, and Functions

The public function is `smbcli_deltree()`. Internal `struct delete_state` tracks the tree, total deletions, and any failure. Callback `delete_fn()` is passed to `smbcli_list()` for recursive directory traversal.

## Control Flow

`smbcli_deltree()` first tries to unlink the target as a file and treats missing paths as success with zero deletions. If deletion is denied, it clears attributes and retries. For directories it builds `path\\*`, deletes matching files via `smbcli_unlink_wcard()`, lists directories including hidden/system entries, recursively calls `delete_fn()`, then removes the directory, again clearing attributes on `NT_STATUS_CANNOT_DELETE`.

## State and Persistence Behavior

The function mutates the remote SMB share by deleting files/directories and changing read-only attributes to normal. Local state is transient C heap strings plus the stack `delete_state`.

## Dependencies and Integration Points

It depends on directory attribute macros, `smbcli_unlink()`, `smbcli_unlink_wcard()`, `smbcli_list()`, `smbcli_setatr()`, `smbcli_rmdir()`, and `smbcli_errstr()`/`smbcli_nt_error()` for error handling.

## Risks and Edge Cases

Path construction uses `strdup()`/`asprintf()` and manual trimming. Some allocation failures in callbacks simply return without setting `failed`, so deletions can be silently skipped. Concurrent directory changes can cause list/delete races. Clearing read-only attributes changes remote metadata even if later deletion fails.

## Test Signals

Tests should cover nonexistent targets, single files, read-only files/directories, hidden/system entries, nested trees, allocation/error injection if possible, and server races where entries disappear during traversal.
