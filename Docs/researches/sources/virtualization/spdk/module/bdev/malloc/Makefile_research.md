# File Research: sources/virtualization/spdk/module/bdev/malloc/Makefile

## Purpose
Builds the SPDK malloc bdev module library.

## Main Contents
Declares shared-object version `8.0`, compiles `bdev_malloc.c` and `bdev_malloc_rpc.c`, sets `LIBNAME = bdev_malloc`, uses `spdk_blank.map`, and includes SPDK common/lib make fragments.

## Dependencies
Depends on SPDK make infrastructure and malloc bdev source files.

## Risks and Notes
This makefile is straightforward build glue for an in-memory bdev module.
