# sources/user-network-fs/samba/source4/torture/basic/rename.c

## Purpose
This file tests rename behavior for open files under different share-delete and access-mask combinations.

## Important APIs, types, and functions
The exported function is `torture_test_rename()`. It uses `smbcli_nt_create_full()`, `smbcli_rename()`, `smbcli_close()`, `smbcli_unlink()`, `torture_assert()`, and `torture_assert_ntstatus_ok()`.

## Control flow
The test clears `\test.txt` and `\test1.txt`, opens `\test.txt` with read access and read share only, and asserts rename fails. It repeats with `NTCREATEX_SHARE_ACCESS_DELETE | NTCREATEX_SHARE_ACCESS_READ` and asserts rename succeeds. Finally it opens with only `SEC_STD_READ_CONTROL` and no sharing and asserts rename succeeds, reflecting semantics where no delete/read/write data access is held.

## State and persistence
Only `\test.txt` and `\test1.txt` are created, renamed, closed, and unlinked. There is no local durable state.

## Dependencies and integration points
The test is a basic torture test relying on NT CreateX share-mode semantics and the higher-level `smbcli_rename()` wrapper. It complements deny/share tests in `denytest.c`.

## Risks
Server behavior around metadata-only opens can be subtle; the third case expects rename success even with share access none because the handle does not request conflicting data/delete access. Cleanup runs after each case but early assertion failure can leave a test file.

## Test signals
The critical signals are first rename failing, second rename succeeding with share-delete, and third rename succeeding with `SEC_STD_READ_CONTROL`.
