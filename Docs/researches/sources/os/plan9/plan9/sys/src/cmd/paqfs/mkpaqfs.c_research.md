# File Research: sources/os/plan9/plan9/sys/src/cmd/paqfs/mkpaqfs.c

Builds a `paqfs` archive from a root file or directory. The format consists of a header, typed blocks, a root directory block, and a trailer containing the root block offset and SHA1 digest.

Files are split into fixed-size data blocks; a pointer block stores each data block offset. Directories recursively serialize child `PaqDir` entries into directory blocks and store those block offsets in a pointer block. Blocks may be deflate-compressed unless `-u` is used.

The header records magic, version, block size, creation time, and label. The block header records magic, stored size, type, encoding, and Adler-32 of unencoded data. The trailer stores magic, root offset, and the accumulated SHA1.

Limitations are tied to block size: each pointer block only holds `blocksize / 4` offsets, and entries larger than a block are skipped with warnings.
