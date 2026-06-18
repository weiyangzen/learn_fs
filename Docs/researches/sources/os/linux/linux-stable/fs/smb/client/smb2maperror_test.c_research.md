# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2maperror_test.c

## Purpose
Provides KUnit coverage for SMB2 status-code lookup correctness.

## Main Responsibilities
- Verify that every generated SMB2 status mapping can be found by `smb2_get_err_map_test()`.
- Compare each returned entry against the expected status code, POSIX error, and status string.

## Key Test Logic
- `test_cmp_map()` performs one lookup and asserts:
  - result is non-null,
  - `smb2_status` matches,
  - `posix_error` matches,
  - `status_string` matches.
- `maperror_test_check_search()` iterates from `0` to `smb2_error_map_num - 1`, checking every exported table entry.
- `maperror_suite` registers the single KUnit case as `smb2_maperror`.

## Coverage Value
This test verifies the binary-search lookup path against every table element. Combined with `smb2_init_maperror()` sort validation, it protects the generated mapping table from broken ordering or lookup regressions.
