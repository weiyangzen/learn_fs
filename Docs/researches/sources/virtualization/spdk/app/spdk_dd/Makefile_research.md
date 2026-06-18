# File Research: sources/virtualization/spdk/app/spdk_dd/Makefile

## Purpose
Builds the `spdk_dd` copy utility.

## Main Contents
- Sets `APP = spdk_dd`.
- Compiles `spdk_dd.c`.
- Links all configured modules plus `event` and `event_bdev`.
- Uses SPDK app make rules and install/uninstall helpers.

## Dependencies
Depends on SPDK bdev/event libraries and all configured modules.

## Filesystem/Block Relevance
Builds a dd-like data mover for copying between files and SPDK bdevs.

## Risks and Notes
- Parent makefile restricts this app to Linux builds.
