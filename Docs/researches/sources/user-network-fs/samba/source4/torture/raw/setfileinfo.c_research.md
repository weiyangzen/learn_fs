# sources/user-network-fs/samba/source4/torture/raw/setfileinfo.c

## Purpose
`setfileinfo.c` is the RAW SMB1 set-file-information torture suite. It validates `smb_raw_setfileinfo()` by handle and `smb_raw_setpathinfo()` by path across metadata levels, rename semantics, EOF/allocation changes, disposition/delete-on-close, archive attributes, and known Windows compatibility quirks.

## Important APIs, types, and functions
The suite entry point is `torture_raw_sfileinfo()`. The main tests are `torture_raw_sfileinfo_base()`, `torture_raw_sfileinfo_rename()`, `torture_raw_sfileinfo_bug()`, `torture_raw_sfileinfo_eof()`, `torture_raw_sfileinfo_eof_access()`, and `torture_raw_sfileinfo_archive()`. It uses `union smb_setfileinfo`, `union smb_fileinfo`, `union smb_open`, `RAW_SFILEINFO_*`, `RAW_FILEINFO_*`, `smb_raw_setfileinfo()`, `smb_raw_setpathinfo()`, `smb_raw_fileinfo()`, `smb_raw_pathinfo()`, `smb_raw_open()`, `create_complex_file()`, and `create_directory_handle()`.

## Control flow
The base test creates separate path-based and fnum-based files under `\testsfileinfo`, sets metadata at many information levels, and immediately queries `ALL_INFO` or the corresponding query level to verify the effect. It covers DOS `SETATTR`/`SETATTRE`, standard/basic timestamps, zero-time "do not change" semantics, invalid directory attributes on files, disposition info, allocation size, EOF size, current byte offset, and mode info. The rename test creates file and directory targets, checks collision and overwrite behavior, validates relative names, rejects `root_fid`, tests open-destination conflicts and delete-on-close conflicts, and skips some handle-directory cases under the `samba3` setting. EOF tests use two SMB connections to verify share-mode blocking for path-based EOF changes, the documented and pass-through EOF levels, Windows W2K8/Win7 exceptions, and handle-based EOF changes. EOF access iterates access masks and requires `SEC_FILE_WRITE_DATA` for handle EOF modification. Archive testing verifies default archive behavior for files, directory archive toggling, and `FILE_ATTRIBUTE_NONINDEXED` masking.

## State and persistence behavior
The file mutates only temporary objects in `\testsfileinfo` and removes them with `smbcli_unlink()` or `smbcli_deltree()`. Per-test state is in SMB handles, delete-on-close bits, timestamps, allocation/EOF sizes, and DOS attributes. Some tests intentionally leave name state changed across assertions to confirm handle identity and path lookup behavior after renames. No server configuration is persisted, but dangerous mode can trigger the legacy W2K3 pathinfo bug probe.

## Dependencies and integration points
This file integrates with the raw SMB torture harness and exercises server implementations behind `libcli/raw`. It depends on Samba status helpers, time conversion helpers, test utilities, target feature flags (`TARGET_IS_W2K8`, `TARGET_IS_WIN7`), and torture settings such as `samba3` and `dangerous`. It is directly relevant to PVFS setfileinfo, SMB1 trans2 passthrough levels, and metadata compatibility behavior shared with SMB2 equivalents.

## Risks and edge cases
The assertion macros reuse local variables and jump to shared cleanup, so changes must preserve variable names and handle lifetimes. Several expected statuses encode Windows bugs or Samba3 exceptions rather than ideal protocol behavior. Path rename tests change `path_fname` and `fnum_fname` aliases temporarily, which is easy to break. EOF tests depend on share-mode timing across two connections. The dangerous bug test is intentionally opt-in because it can leave a problematic file on affected servers.

## Test signals
Passing signals include exact NTSTATUS results for each set-info level, unchanged timestamps when zero values are supplied, correct `delete_pending` and `nlink` transitions, path/handle rename name-info agreement, share violations for blocked EOF changes, access-denied without write-data permission, and correct archive-bit state on files and directories.
