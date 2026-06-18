# sources/user-network-fs/samba/source4/libcli/clitrans2.c

## Purpose

`clitrans2.c` provides convenience wrappers for SMB TRANS2 file and path information queries. It fetches standard path info, all-info path/file metadata, file names by fnum, and alternate 8.3 names.

## Important APIs, Types, and Functions

Exports are `smbcli_qpathinfo()`, `smbcli_qpathinfo2()`, `smbcli_qfilename()`, `smbcli_qfileinfo()`, and `smbcli_qpathinfo_alt_name()`. They use `union smb_fileinfo` with levels `RAW_FILEINFO_STANDARD`, `RAW_FILEINFO_ALL_INFO`, `RAW_FILEINFO_NAME_INFO`, and `RAW_FILEINFO_ALT_NAME_INFO`.

## Control Flow

Each function creates a short-lived talloc context, fills the appropriate input path or fnum, calls `smb_raw_pathinfo()` or `smb_raw_fileinfo()`, frees the context, and copies selected outputs to optional caller pointers. Time values from all-info levels are converted from NT time to Unix time. Name-returning helpers duplicate strings for the caller.

## State and Persistence Behavior

The operations are read-only against the remote share. Locally they allocate temporary talloc memory and return heap-allocated strings from `strdup()` for name outputs.

## Dependencies and Integration Points

The file depends on raw path/file info APIs, NT time conversion, `struct smbcli_tree`, and caller conventions from `libcli.h`.

## Risks and Edge Cases

The `ino` output parameter in `smbcli_qpathinfo2()` is ignored, while `smbcli_qfileinfo()` sets it to zero. String outputs use `strdup()` and must be freed by callers; allocation failure is not checked before returning OK. `smbcli_qpathinfo_alt_name()` returns `smbcli_nt_error(tree)` on raw failure rather than the local status, which can differ.

## Test Signals

Tests should cover all query levels against files and directories, optional null output parameters, alternate-name absence/presence, Unicode names, allocation failure if injectable, and consistency between path and fnum all-info results.
