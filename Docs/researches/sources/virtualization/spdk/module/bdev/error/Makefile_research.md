# File Research: sources/virtualization/spdk/module/bdev/error/Makefile

This makefile builds the `bdev_error` module from `vbdev_error.c` and `vbdev_error_rpc.c`. It sets shared-library version `8.0`, uses SPDK's blank map file, and includes the standard SPDK library build rules.

The parent bdev makefile always includes `error`, so error-injection virtual bdev support is part of the default bdev module build set. The implementation and RPC files are outside this work item's file list and were not researched here.
