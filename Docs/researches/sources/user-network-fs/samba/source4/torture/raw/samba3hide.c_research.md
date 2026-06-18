# sources/user-network-fs/samba/source4/torture/raw/samba3hide.c

## Purpose
This file contains Samba3 compatibility tests for permission-based hiding and close-error propagation. `torture_samba3_hide()` verifies `hide unreadable` and `hide unwriteable` share behavior using Unix permissions. `torture_samba3_closeerr()` verifies that close returns an access error when delete-on-close cannot be completed because parent directory permissions were removed.

## Important APIs, Types, And Functions
`init_unixinfo_nochange()` prepares a `RAW_SFILEINFO_UNIX_BASIC` structure with all non-permission fields set to Samba Unix-extension "no change" sentinel values. `smbcli_setup_unix()` negotiates CIFS Unix extensions by querying `RAW_QFS_UNIX_INFO` and setting `RAW_SETFS_UNIX_INFO`. `smbcli_chmod()` applies Unix permissions with `smb_raw_setpathinfo()`.

Visibility and access helpers include `is_visible()` using `smbcli_list()`, `is_readable()`, `is_writeable()`, and `smbcli_file_exists()`. The tests also use `torture_second_tcon()` to connect to special shares named `hideunread` and `hideunwrite`.

## Control Flow
`torture_samba3_hide()` enables Unix extensions, opens secondary tree connections to the hide shares, creates `torture_samba3_hide.txt`, and verifies three permission states. With read/write user permissions, the file must be visible and accessible everywhere. With read-only permissions, it must remain visible on the normal and hide-unreadable shares but disappear from the hide-unwriteable share. With no permissions, it must remain visible only on the normal share and be hidden from both special shares. The test restores permissions and unlinks the file.

`torture_samba3_closeerr()` creates `closeerr.dir\closerr.txt`, opens it with delete sharing, sets delete-on-close, chmods the parent directory to `000`, and then closes the file. It restores directory permissions, deletes the tree, and asserts that close returned `NT_STATUS_ACCESS_DENIED`.

## State And Persistence Behavior
The hide test mutates Unix mode bits on a test file and uses multiple tree connections to shares that must be configured differently. The close-error test mutates parent directory permissions to force cleanup failure, then restores owner read/write/execute before deleting. If interrupted between chmod and restore, server-side permissions may need manual cleanup.

## Dependencies And Integration Points
These tests depend on Samba Unix extensions, POSIX permission semantics, configured shares named `hideunread` and `hideunwrite`, and raw setpathinfo/setfsinfo support. They are registered in `raw.c` as `samba3hide` and `samba3closeerr`.

## Risks And Edge Cases
The tests are environment-sensitive: missing Unix extensions, differently named shares, non-POSIX backing stores, or unexpected ACL overlays can produce failures unrelated to the raw SMB client code. `smbcli_file_exists()` treats any `getatr` failure as nonexistence, which is good enough for this purpose but not a general existence test. Close-error behavior depends on the server surfacing delete-on-close failures at close time.

## Test Signals
Success is a matrix of visibility/read/write outcomes for each permission state plus an exact `NT_STATUS_ACCESS_DENIED` on forced close failure. Failures name the specific visibility or access expectation that was violated.
