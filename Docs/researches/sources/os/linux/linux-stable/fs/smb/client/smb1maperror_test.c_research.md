# File Research: sources/os/linux/linux-stable/fs/smb/client/smb1maperror_test.c

This file is a KUnit test module for SMB1 error-map lookup coverage.

Test strategy:
- Defines a macro that iterates every exported test array entry and searches for that entry by key.
- Compares returned entries field-by-field against the expected table element.
- Covers:
  - `ntstatus_to_dos_map`,
  - `mapping_table_ERRDOS`,
  - `mapping_table_ERRSRV`.

Assertions:
- `KUNIT_ASSERT_NOT_NULL()` verifies each lookup succeeds.
- NT status mapping checks DOS class, DOS code, NT status, and NT error string.
- SMB-to-POSIX mapping checks SMB error code and POSIX code.

Dependencies:
- Requires `CONFIG_SMB1_KUNIT_TESTS`, which causes `smb1maperror.c` to export its otherwise-static tables and search wrappers for this test module.

Value:
- This test ensures binary-search lookup coverage across every generated mapping entry. It complements the runtime sorted-table checks in `smb1_init_maperror()`.
