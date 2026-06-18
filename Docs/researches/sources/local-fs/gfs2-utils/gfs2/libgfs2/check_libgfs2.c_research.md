# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/check_libgfs2.c

This is the Check test runner for libgfs2.

It declares suite factories for metadata, on-disk conversion, resource groups, and filesystem operations:
- `suite_meta()`
- `suite_ondisk()`
- `suite_rgrp()`
- `suite_fs_ops()`

`main()` creates an `SRunner` from the metadata suite, adds the other suites, runs all tests using `CK_ENV`, returns `1` if any tests failed, and `0` otherwise.

The file is narrow orchestration glue for the unit-test binary configured in `checks.am`.
