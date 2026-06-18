# File Research: sources/virtualization/spdk/app/fio/Makefile

## Purpose
Recursive makefile for SPDK fio plugins. It builds both the direct NVMe fio plugin and the bdev fio plugin.

## Main Contents
- Sets `SPDK_ROOT_DIR` relative to `app/fio`.
- Includes `mk/spdk.common.mk`.
- Adds `nvme` and `bdev` subdirectories to `DIRS-y`.
- Delegates `all` and `clean` to `mk/spdk.subdirs.mk`.

## Dependencies
Uses SPDK's common and recursive subdirectory make infrastructure.

## Filesystem/Block Relevance
This file is the build entry point for fio engines used to benchmark SPDK block devices and SPDK NVMe paths.

## Risks and Notes
- It has no conditional logic itself; enablement is controlled by the parent `app/Makefile`.
