# File Research: sources/virtualization/spdk/module/bdev/null/Makefile

## Purpose
Builds the SPDK null bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `bdev_null.c` and `bdev_null_rpc.c`, sets `LIBNAME = bdev_null`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends on SPDK make infrastructure and the null bdev source files that are outside this group's listed sources.

## Risks and Notes
Only the makefile is in this work item. The actual null bdev behavior is defined in `bdev_null.c` and `bdev_null_rpc.c`, which are referenced here but not part of this grouped file list.
