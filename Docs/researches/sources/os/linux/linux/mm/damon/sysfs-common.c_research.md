# File Research: sources/os/linux/linux/mm/damon/sysfs-common.c

Common sysfs support code for DAMON.

Implemented object:
- `damon_sysfs_ul_range`, a kobject-backed unsigned long range with `min` and `max` fields.

Key functions:
- `damon_sysfs_ul_range_alloc()` allocates and initializes a range object.
- `min_show()` / `min_store()` expose and update the minimum value.
- `max_show()` / `max_store()` expose and update the maximum value.
- `damon_sysfs_ul_range_release()` frees the containing range object.

Exports:
- Global `damon_sysfs_lock`.
- `damon_sysfs_ul_range_ktype`, with release callback, `kobj_sysfs_ops`, and default `min`/`max` attribute group.

This file provides a small reusable sysfs building block used by larger DAMON sysfs scheme/configuration code.
