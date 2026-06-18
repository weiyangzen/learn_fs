# File Research: sources/virtualization/nbd/lfs.h

Large-file and sync feature compatibility header.

When `NBD_LFS` is enabled, it defines `_FILE_OFFSET_BITS 64`, ensures `_LARGEFILE_SOURCE`, and maps `PARAM_OFFT` to `PARAM_INT64`; otherwise it maps to `PARAM_INT`.

When `HAVE_SYNC_FILE_RANGE` is defined, it enables `USE_SYNC_FILE_RANGE` and `_GNU_SOURCE`.
