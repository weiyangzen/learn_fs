# File Research: sources/os/bsd/freebsd-src/sbin/growfs/tests/legacy_test.pl

`legacy_test.pl` is a root-only TAP test for growfs.

Key behavior:
- Plans 19 tests.
- Creates a 40 MiB md device and cleans it up in `END`.
- Uses `gpart restore` to resize an `a` partition.
- Initializes UFS1 and UFS2 filesystems with `newfs -O`.
- Validates filesystems with `fsck_ffs -Ffy`, accepting exit status 0 or 7.
- Grows from 10 MiB to 20 MiB with zero-filled new space.
- Grows from 20 MiB to 30 MiB with patterned garbage-filled new space.
- Runs `growfs -y` for both growth steps.
- Handles growfs output that reports unallocatable trailing sectors by zeroing those sectors before fsck.
- Skips all tests when not run as UID 0.

This test exercises both clean and garbage-filled expansion regions for UFS1 and UFS2.
