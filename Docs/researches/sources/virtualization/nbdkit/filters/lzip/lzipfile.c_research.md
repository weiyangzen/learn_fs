# File Research: sources/virtualization/nbdkit/filters/lzip/lzipfile.c

Wraps liblzma and lzip member indexing for the lzip filter. `lzipfile_open()` checks file magic, builds a member index, records maximum uncompressed block size, and logs archive statistics.

`setup_index()` scans the lzip archive backward from the file end. For each member, it reads the 20-byte footer, extracts uncompressed data size and compressed member size as little-endian 64-bit values, validates size bounds, moves to the member start, verifies header magic, and prepends the member to the index. It finalizes offsets after all members are found.

`lzipfile_read_block()` locates the member containing an uncompressed offset, initializes `lzma_lzip_decoder()`, allocates an output buffer exactly the member’s uncompressed size, streams compressed member bytes from `next->pread()` in 1 MiB chunks, and returns the full decompressed member.

Errors clean up the lzma stream, compressed buffer, and output buffer.
