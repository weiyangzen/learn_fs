# File Research: sources/os/linux/linux/fs/smb/client/smb2maperror_test.c

This file provides KUnit coverage for SMB2 status-to-errno mapping lookup.

Primary responsibilities:
- Iterate every exported SMB2 mapping-table entry.
- Look up each status with `smb2_get_err_map_test()`.
- Assert that the returned mapping matches status code, POSIX errno, and status string.

Important control flow:
- `test_cmp_map()` performs one lookup and validates all fields with KUnit assertions/expectations.
- `maperror_test_check_search()` loops from `0` to `smb2_error_map_num - 1`.
- `maperror_suite` registers the single test case under suite name `smb2_maperror`.

Dependencies:
- KUnit, CIFS/SMB2 test exports from `smb2maperror.c`, `smb2glob.h` mapping structure, and SMB2 prototype declarations.

Research notes:
- This test is primarily a regression check for binary-search reachability across the generated sorted table.
- It does not test unmapped statuses or logging behavior; it verifies that every table entry can be found and returned intact.
