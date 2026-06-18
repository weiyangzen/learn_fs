# File Research: sources/virtualization/spdk/module/bdev/iscsi/Makefile

## Purpose
Builds the SPDK iSCSI bdev module library.

## Main Contents
Declares shared-object version `8.0`, adds `lib/bdev` to include paths, suppresses warning-as-error behavior for CentOS 7 libiscsi inline declarations, compiles `bdev_iscsi.c` and `bdev_iscsi_rpc.c`, names the library `bdev_iscsi`, and uses `spdk_blank.map`.

## Dependencies
Depends on SPDK make infrastructure and external libiscsi headers/libraries supplied elsewhere in the build.

## Risks and Notes
The `-Wno-error` is an environment compatibility workaround and should not hide module-specific warnings unintentionally.
