# File Research: sources/virtualization/spdk/app/fio/nvme/Makefile

## Purpose
Builds the direct SPDK NVMe fio plugin.

## Main Contents
- Sets `FIO_PLUGIN := spdk_nvme`.
- Compiles `fio_plugin.c`.
- Links socket modules, `nvme`, and `vmd`.
- Includes `mk/spdk.fio.mk`.

## Dependencies
Depends on SPDK socket modules, NVMe library, VMD library, common/module make fragments, and fio plugin make rules.

## Filesystem/Block Relevance
Builds the fio engine that bypasses SPDK bdev and drives NVMe namespaces directly.

## Risks and Notes
- Direct NVMe support differs from the bdev plugin: configuration is supplied through fio file names and plugin options rather than SPDK bdev JSON.
