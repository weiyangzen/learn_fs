# File Research: sources/os/linux/linux/mm/damon/sysfs-common.h

Common declarations for DAMON sysfs support.

Defines:
- External `damon_sysfs_lock`.
- `struct damon_sysfs_ul_range`, containing a kobject plus unsigned long `min` and `max`.
- Allocation/release declarations and external `damon_sysfs_ul_range_ktype`.

Also declares shared scheme sysfs integration types and functions:
- `struct damon_sysfs_schemes`.
- Allocation/removal helpers for scheme directories.
- `damon_sysfs_add_schemes()`.
- Scheme stat update helpers.
- Region population/clear helpers for scheme results.
- Quota score/effective quota update helpers.

This header connects the simple range object from `sysfs-common.c` with the fuller DAMON sysfs scheme implementation in other files.
