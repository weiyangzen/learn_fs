# File Research: sources/virtualization/spdk/lib/blob/Makefile

This Makefile builds the SPDK `blob` library from `blobstore.c`, `request.c`, `zeroes.c`, and `blob_bs_dev.c`. It sets shared-object version `14.0`, names the library `blob`, and uses `spdk_blob.map` for symbol exports.

Research notes: the listed group includes only the blob-backed `bs_dev` adapter file from this library, not the main blobstore implementation.
