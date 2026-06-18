# File Research: sources/virtualization/spdk/module/bdev/Makefile

This makefile is the subdirectory dispatcher for SPDK bdev modules. It includes common SPDK make definitions and then selects bdev module directories based on build configuration and OS.

Always-built modules include `delay`, `error`, `gpt`, `lvol`, `malloc`, `null`, `nvme`, `passthru`, `raid`, `split`, and `zone_block`. Optional modules include `xnvme`, `crypto`, `ocf`, `uring`, `rbd`, and `daos` behind their respective `CONFIG_*` variables. On Linux it also builds `aio` and `ftl`, plus `iscsi` and `virtio` when enabled; on FreeBSD it builds `aio`. The `all` and `clean` targets recurse through `$(DIRS-y)` via `mk/spdk.subdirs.mk`.
