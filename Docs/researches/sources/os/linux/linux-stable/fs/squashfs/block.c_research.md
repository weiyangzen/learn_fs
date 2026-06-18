# File Research: sources/os/linux/linux-stable/fs/squashfs/block.c

## Summary
Implements low-level reads of compressed or uncompressed Squashfs metadata and data blocks from the block device, including BIO construction, optional compressed-page caching, metadata length decoding, and dispatch to the selected decompressor.

## Key APIs
- `squashfs_read_data()`: reads one metadata block or file data block and fills a `squashfs_page_actor`.

## Important Behavior
Metadata blocks have a two-byte on-disk length header; file data block lengths are supplied from inode block lists. Both encodings use a high bit to mark uncompressed storage.

`squashfs_bio_read()` rounds requested byte ranges to the device block size, allocates one BIO page per covered page, reuses uptodate pages from `msblk->cache_mapping` when available, and returns the intra-device-block offset.

When the device block size is one page, `squashfs_bio_read_cached()` can cache boundary pages that were fetched only because an unaligned compressed block shared them with adjacent data. With `CONFIG_SQUASHFS_COMP_CACHE_FULL`, it attempts to cache all fetched compressed pages.

Compressed blocks call `msblk->thread_ops->decompress()`. Uncompressed blocks copy bytes directly from the BIO into the page actor.

## Risks
Bounds checks against `msblk->bytes_used` are critical because the source length comes from on-disk metadata. The compressed-page cache path manipulates folios carried in BIOs; failure handling must avoid leaking pages or leaving unlocked folios in the cache mapping.
