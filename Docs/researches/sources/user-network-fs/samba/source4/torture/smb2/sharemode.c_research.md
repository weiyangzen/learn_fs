# sources/user-network-fs/samba/source4/torture/smb2/sharemode.c

## Purpose

`sharemode.c` implements SMB2 torture tests for share-mode conflict behavior and includes two manual harnesses for cross-filesystem or external-access experiments. Automated tests verify that the interaction between a first open's share access and a second open's desired access matches SMB semantics, and vice versa. The file exports `torture_smb2_sharemode_init()` for the `smb2.sharemode` suite plus simple manual tests `torture_smb2_hold_sharemode()` and `torture_smb2_check_sharemode()` that are registered by the top-level suite.

## Important APIs, Types, and Functions

Important types are `struct hold_sharemode_info`, `struct sharemode_info`, `struct smb2_tree`, `struct smb2_create`, `struct smb2_handle`, `union smb_setfileinfo`, and tevent signal types. The file relies on `torture_smb2_connection()`, `torture_smb2_testdir()`, `smb2_create()`, `smb2_read()`, `smb2_util_write()`, `smb2_setinfo_file()`, `smb2_util_close()`, `smb2_util_unlink()`, `smb2_deltree()`, `smb2_util_share_access()`, `torture_setting_string()`, and `smb_strtoul()`.

`hold_sharemode_table` lists all share-mode combinations for files held open in `sharemode_hold_test`: none, R, W, D, RW, RD, WD, and RWD. `sharemode_table` is a large expected-result matrix mapping share-mode strings to desired access masks and whether a second create should succeed.

## Control Flow

`torture_smb2_hold_sharemode()` is a manual test. It connects, registers a SIGINT handler, creates a directory, opens one file for each share mode with `SEC_RIGHTS_FILE_ALL`, then waits in `tevent_loop_wait()` until interrupted. On exit it marks each file `delete_on_close`, closes handles, tolerates `NT_STATUS_OBJECT_NAME_NOT_FOUND` when an external client deleted a file, and deletes the directory tree.

`torture_smb2_check_sharemode()` is also manual/config-driven. It reads torture settings `sharemode`, `access`, `filename`, and `operation`, opens a file with the requested share/access values, then optionally performs read, write, and delete operations based on operation letters R/W/D. It is useful when another process has already opened the file outside Samba.

`test_smb2_sharemode_access()` is automated. For each `sharemode_table` entry, it first opens `test_sharemode` with full access and the entry's share mode, then attempts a second open from another SMB2 tree with the entry's desired access and full sharing. It expects `NT_STATUS_OK` when `expect_ok` is true and `NT_STATUS_SHARING_VIOLATION` otherwise. It closes the first handle every iteration and closes the second only when the second open succeeded.

`test_smb2_access_sharemode()` reverses the matrix. The first open uses the entry's desired access and full sharing; the second open requests full access with the entry's share mode. It expects the same OK/sharing-violation result, exercising both directions of Samba share-mode compatibility checks.

`test_smb2_bug14375()` covers a regression where an initial stat-like open with `SEC_FILE_READ_ATTRIBUTE` and share-none must not poison later opens. It checks both orders: stat/share-none first followed by data opens, then data open first followed by stat/share-none and another data open.

## State and Persistence Behavior

Automated tests create and unlink a single `test_sharemode` file repeatedly. Manual hold mode creates a persistent directory and keeps handles open until SIGINT so external clients can probe behavior; cleanup attempts to delete all files and the directory. `check-sharemode` can intentionally delete the configured file when operation includes D. No repository state is changed; all persistence is on the target SMB share.

## Dependencies and Integration Points

The automated suite integrates through `torture_smb2_sharemode_init()` and uses `torture_suite_add_2smb2_test()` for two-tree conflict tests and `torture_suite_add_1smb2_test()` for the regression. The manual functions are registered in `smb2.c` as top-level simple SMB2 tests. The file depends on tevent for SIGINT handling and on Samba security access-mask constants to express desired access. It assumes the server and backend enforce share-mode semantics consistently across separate SMB2 tree connections.

## Risks

The matrix encodes subtle protocol policy: some metadata-oriented rights such as EA, attributes, read-control, write-DAC, write-owner, and synchronize are expected to pass despite R/W/D sharing restrictions, while data read/write/delete bits are expected to conflict based on the share flags. Regressions can be caused by server share-mode logic, VFS/open-file-description behavior, or backend filesystems that enforce or bypass share modes differently. Manual tests intentionally block until interrupted, so they are unsuitable for unattended runs unless explicitly selected.

## Test Signals

The strongest signals are exact `NT_STATUS_OK` versus `NT_STATUS_SHARING_VIOLATION` on the second create for every matrix entry, successful cleanup closes, and bug14375's absence of unexpected sharing violations. Manual tests signal through successful open/read/write/delete operations and comments printed while waiting or cleaning up.
