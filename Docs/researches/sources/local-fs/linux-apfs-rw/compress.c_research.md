# File Research: sources/local-fs/linux-apfs-rw/compress.c

This file implements transparent read support for APFS compressed files stored through `com.apple.decmpfs` and optionally `com.apple.ResourceFork`.

Supported algorithms:
- zlib attribute/resource.
- LZVN attribute/resource.
- plain attribute/resource.
- LZFSE attribute/resource.
- lzbitmap attribute/resource.

`apfs_compress_file_open()` rejects write opens with `-EOPNOTSUPP`, reads the decmpfs header from xattrs, validates the algorithm, allocates a 64 KiB decompression buffer, and obtains compressed data either from the compressed xattr or resource fork.

`apfs_compress_file_read_block()` maps the APFS compressed layout to one decompressed 64 KiB logical block. It handles resource-fork block tables, inline attribute compression, and per-algorithm framing quirks. It then decompresses or copies data into the cached buffer.

`apfs_compress_file_read_from_block()` clamps reads to the uncompressed size, prereads nonsparse dstreams for xattr/resource data, loads the target compressed block if not cached, and copies the requested slice.

`apfs_compress_file_read_page()` fills one page through repeated block reads. The address-space operations expose either `read_folio` or `readpage` depending on kernel version, zeroing the remainder and marking the page uptodate on success.

`apfs_compress_file_operations` provides open, llseek, read_iter, release, and mmap. A comment notes these operations lack proper locking. Writes are intentionally unsupported rather than transparently decompressing/replacing content.

`apfs_compress_get_size()` reads the decmpfs header and reports the uncompressed size if the algorithm is supported.

Research relevance: this file provides read-path integration for compressed APFS files and shows a clear limitation: compressed files are read-only through this driver.
