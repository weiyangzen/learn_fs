# File Research: sources/local-fs/kdave-linux/fs/btrfs/zlib.c

## Role

`zlib.c` implements Btrfs zlib compression and decompression using kernel zlib streams and Btrfs compressed-bio helpers.

## Workspace Management

`struct workspace` contains a `z_stream`, an auxiliary buffer, buffer size, list node, and compression level. Workspaces are allocated through Btrfs compression workspace infrastructure.

`zlib_alloc_workspace()` allocates zlib deflate/inflate workspace memory and a staging buffer. On s390 with zlib DFLTCC acceleration, `need_special_buffer()` may allocate a 4-page buffer to improve hardware compression performance unless the filesystem minimum folio size is already large enough.

`zlib_free_workspace()` releases stream workspace, buffer, and wrapper object.

## Compression Path

`zlib_compress_bio()` compresses a file range into the compressed bio:

- Initializes deflate at the requested level.
- Allocates compressed output folios.
- Feeds input from filemap folios directly, or via the special staging buffer for s390 acceleration.
- Calls `zlib_deflate()` with `Z_SYNC_FLUSH`, then finalizes with `Z_FINISH`.
- Adds full and partial compressed folios to the bio.
- Rejects compression if output grows beyond input or becomes too large for the original range.

Expansion detection returns `-E2BIG`, causing upper layers to store data uncompressed.

## Decompression Paths

`zlib_decompress_bio()` inflates compressed bio contents into page-cache targets using `btrfs_decompress_buf2page()`. It maps compressed input folios one at a time and refills zlib input as needed.

`zlib_decompress()` handles smaller direct decompression into a destination folio, intended for cases where input and output are bounded by one sector. It zero-fills the destination tail if decompression produces too little data and returns `-EIO`.

Both decompression paths detect zlib headers without preset dictionaries and can use negative window bits to skip the Adler-32 check.

## Error Handling

Initialization or stream errors are logged with root id, inode number, and offset. Compression failures return `-EIO`, allocation failures return `-ENOMEM`, and ineffective compression returns `-E2BIG`.

## Compression Levels

`btrfs_zlib_compress` exposes levels 1 through 9 with `BTRFS_ZLIB_DEFAULT_LEVEL`.
