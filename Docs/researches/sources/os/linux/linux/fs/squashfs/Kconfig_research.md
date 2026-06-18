# File Research: sources/os/linux/linux/fs/squashfs/Kconfig

Defines the Linux kernel configuration surface for SquashFS 4.0, a compressed read-only filesystem requiring `BLOCK`.

Key options cover file-data decompression strategy (`SQUASHFS_FILE_CACHE` intermediate buffer vs `SQUASHFS_FILE_DIRECT` direct page-cache output), decompressor concurrency (`single`, dynamic `multi`, and `percpu`), optional mount-time `threads=`, xattrs, compression backends, device block size, embedded cache sizing, and fragment cache size.

Notable local option: `SQUASHFS_COMP_CACHE_FULL`, which enables caching all compressed block pages for repeated-read workloads at the cost of memory use.

Compression backend options select kernel libraries: zlib, LZ4, LZO, XZ, and ZSTD. Defaults favor zlib and conservative memory use.
