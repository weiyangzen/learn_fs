# File Research: sources/virtualization/spdk/app/fio/bdev/Makefile

## Purpose
Builds the `spdk_bdev` fio ioengine plugin from `fio_plugin.c`.

## Main Contents
- Includes SPDK common and module make fragments.
- Sets `FIO_PLUGIN := spdk_bdev`.
- Compiles `fio_plugin.c`.
- Links all SPDK bdev modules plus `event` and `event_bdev`.
- Includes `mk/spdk.fio.mk` for fio plugin build rules.

## Dependencies
Depends on `$(ALL_MODULES_LIST)`, SPDK event framework, event bdev support, and SPDK's fio plugin make fragment.

## Filesystem/Block Relevance
Produces the fio plugin that drives SPDK bdevs through the bdev layer, covering malloc, NVMe, file, zoned, and other configured bdev modules.

## Risks and Notes
- Linking `ALL_MODULES_LIST` makes the plugin broadly capable but dependent on configured module availability.
