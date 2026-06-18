# File Research: sources/os/linux/linux/fs/squashfs/block.c

Implements the low-level path for reading compressed or uncompressed SquashFS metadata/data blocks from the block device.

`squashfs_bio_read()` builds BIOs aligned to the device block size, optionally reusing a page-cache mapping for compressed block pages. `squashfs_bio_read_cached()` avoids rereading cached folios and caches partial edge pages; with `CONFIG_SQUASHFS_COMP_CACHE_FULL`, it also tries to cache every page in the BIO.

`squashfs_read_data()` decodes metadata block length headers when needed, validates block bounds against `bytes_used`, submits I/O, and either copies uncompressed data into a page actor or calls the selected decompressor thread ops.

Important failure behavior: read or decompression failures log the failing block and panic when mounted with `errors=panic`.
