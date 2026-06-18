# sources/user-network-fs/samba/source4/libcli/clifile.c

## Purpose

`clifile.c` provides synchronous convenience wrappers for SMB1 file and directory operations. It maps POSIX-like helper calls and Samba test helpers onto raw SMB open, close, rename, delete, attribute, lock, truncate, path, disk, and temporary-file requests.

## Important APIs, Types, and Functions

Exports include Unix extension helpers `smbcli_unix_symlink()`, `smbcli_unix_hardlink()`, `smbcli_unix_chmod()`, `smbcli_unix_chown()`, file operations `smbcli_rename()`, `smbcli_unlink()`, `smbcli_unlink_wcard()`, `smbcli_mkdir()`, `smbcli_rmdir()`, `smbcli_nt_delete_on_close()`, `smbcli_nt_create_full()`, `smbcli_open()`, `smbcli_close()`, locks/unlocks with 32-bit and 64-bit offsets, `smbcli_getattrE()`, `smbcli_getatr()`, `smbcli_setatr()`, `smbcli_fsetatr()`, `smbcli_ftruncate()`, `smbcli_chkpath()`, `smbcli_dskattr()`, and `smbcli_ctemp()`.

## Control Flow

Most functions fill a raw SMB union at a specific information level and call the matching `smb_raw_*` function. `smbcli_open()` converts POSIX flags into SMBopenX open functions and access modes. Wildcard unlink lists matching entries and deletes each resolved name. 64-bit lock helpers fall back to 32-bit locks when the negotiated transport lacks `CAP_LARGE_FILES`. Query helpers copy selected output fields to optional caller pointers.

## State and Persistence Behavior

These functions mutate remote files/directories, locks, attributes, timestamps, delete-on-close flags, and file sizes. They maintain little local state beyond temporary talloc contexts and return fnums from successful opens. Wildcard delete tracks the first failed name for debugging but does not return it to callers.

## Dependencies and Integration Points

The file depends on raw SMB1 unions/functions from `libcli/raw`, `struct smbcli_tree`, negotiated transport capabilities, Unix permission conversion, and `smbcli_list()` for wildcard deletion.

## Risks and Edge Cases

Some wrappers return `-1` instead of NTSTATUS, losing details. `smbcli_unlink_wcard()` initializes `state->status` to zero through talloc, which corresponds to OK, and only preserves the first delete failure. `smbcli_chkpath()` uses `strdup()` without null checks. Large `off_t` values can be truncated on fallback 32-bit lock paths.

## Test Signals

Coverage should include every wrapper against a test share: Unix extensions, wildcard delete, create dispositions, sharing modes, delete-on-close, lock conflict behavior, large-file locks with and without capability, timestamp/attribute round trips, truncation, disk attribute queries, and temporary file creation.
