# File Research: sources/virtualization/spdk/module/blob/bdev/Makefile

Builds the blobstore bdev adapter library.

Key elements:
- Defines shared object version `SO_VER := 14`, `SO_MINOR := 0`.
- Compiles `blob_bdev.c`.
- Produces library `blob_bdev`.
- Uses `spdk_blob_bdev.map` as the export map.

Dependencies:
- Includes SPDK common and library make fragments.

Research notes:
- This is the build unit for `spdk_bdev_create_bs_dev()` and related blobstore block-device adapter functions.
