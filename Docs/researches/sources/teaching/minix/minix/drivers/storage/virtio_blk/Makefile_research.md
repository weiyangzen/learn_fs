# File Research: sources/teaching/minix/minix/drivers/storage/virtio_blk/Makefile

## Purpose

Builds the MINIX virtio block driver service.

## Build Role

Defines `PROG=virtio_blk` from `virtio_blk.c`. Links against `libblockdriver`, `libsys`, `libmthread`, and `libvirtio`, then includes `minix.service.mk`.

## Dependencies

Requires the multithreaded blockdriver support and the MINIX virtio library.

## Risks

The library list is essential: the driver uses blockdriver_mt worker sleep/wakeup and virtio queue/device APIs directly.
