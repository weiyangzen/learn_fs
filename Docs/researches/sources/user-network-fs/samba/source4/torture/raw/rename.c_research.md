# sources/user-network-fs/samba/source4/torture/raw/rename.c

## Purpose
This file implements raw SMB rename and hardlink torture tests. It covers classic `SMBmv`, `SMBntrename`, hardlink creation, copy-style NT rename, case-only rename behavior, invalid flags, attribute filtering, and directory rename interactions with open children, open directory handles, long names, and directory streams.

## Important APIs, Types, And Functions
The suite factory `torture_raw_rename()` registers local tests `test_mv`, `test_ntrename`, `test_nthardlink`, `test_osxrename`, and `test_dir_rename`, plus externally implemented `test_trans2rename()` and `test_nttransrename()` from `oplock.c`. Core types are `union smb_rename`, `union smb_open`, and `union smb_fileinfo`. The tests use `smb_raw_rename()`, `smb_raw_open()`, `smb_raw_pathinfo()`, `smbcli_close()`, `smbcli_unlink()`, `smbcli_deltree()`, `create_complex_file()`, and `torture_set_file_attribute()`.

## Control Flow
`test_mv()` validates simple SMBmv behavior: rename fails while the source is open without delete sharing, succeeds with `SHARE_ACCESS_DELETE`, supports case-only renames, works after session exit, allows self-rename, and reports not-found for absent sources. `test_osxrename()` focuses on case-changing rename compatibility by probing/deleting an existing uppercase spelling before renaming.

`test_ntrename()` exercises `RAW_RENAME_NTRENAME`: sharing violation while open, wildcard syntax rejection, hidden-attribute filtering, copy flag behavior, attribute independence between source and copy, invalid flag handling with Win7-specific expectations, unknown cluster-size tolerance, move-cluster rejection, and a warning loop over many unsupported flags. `test_nthardlink()` creates a hardlink with `RENAME_FLAG_HARD_LINK` and verifies `nlink` and shared attributes. `test_dir_rename()` checks that a directory containing an open child file cannot be renamed, but a directory can be renamed while a separate directory handle or a stream on the directory is open in the tested access modes.

## State And Persistence Behavior
The suite uses `\testrename` and removes it after each test. It creates files, directories, hardlinks, copies, attributes, and streams, and often calls `smb_raw_exit()` before deleting the tree to flush session state. Some tests intentionally hold handles open across rename attempts to exercise share-mode and delete-sharing semantics.

## Dependencies And Integration Points
Dependencies include raw SMB rename/open/pathinfo APIs, torture helper functions, target detection through `TARGET_IS_WIN7()`, and nested tests implemented in the oplock module. The suite is registered by `raw.c` as the raw rename sub-suite.

## Risks And Edge Cases
Expected statuses differ between Windows versions for invalid NT rename flags. Case-only rename behavior depends on server case-preservation and case-sensitivity settings. Hardlink checks require filesystem support for links. Directory stream behavior and long-name open regressions are compatibility-sensitive. The invalid-flag loop logs warnings rather than failing most cases, so it is diagnostic coverage rather than strict exhaustive validation.

## Test Signals
The test asserts exact NTSTATUS outcomes for each operation and checks returned file metadata such as final filename, link count, and attributes. Cleanup failure can leave `\testrename` artifacts that influence later runs, so the repeated `torture_setup_dir()` and `smbcli_deltree()` calls are important signals for isolation.
