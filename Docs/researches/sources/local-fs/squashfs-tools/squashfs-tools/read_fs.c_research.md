# File Research: sources/local-fs/squashfs-tools/squashfs-tools/read_fs.c

Append-mode reader for existing Squashfs images. `read_block()` reads compressed metadata blocks, validates encoded compressed size against expected output length, decompresses through the selected compressor, and returns uncompressed length.

`read_super()` validates the superblock magic/version, rejects unsupported old big-endian and future filesystem versions, resolves compressor support, reads compressor options when present, and prints filesystem feature summary unless quiet.

`scan_inode_table()` decompresses the inode table, locates the root inode block, validates root directory inode type and id indexes, scans all earlier inodes, counts object types, adds uid/gid ids, records regular file block lists through `add_file()`, validates fragment indexes, tracks uncompressed file/directory sizes, and builds append fragment-file mapping.

`squashfs_readdir()` decompresses root directory metadata, validates directory counts and name lengths, and pushes existing root entries via callback. Table readers handle id table, fragment table, and inode lookup table with index-table byte checks and endian swapping.

Top-level `read_filesystem()` reads xattrs, fragment/lookup/id tables, scans inodes, extracts preserved compressed inode/directory prefixes and uncompressed root/directory cache data needed to append to the old filesystem. Returns the inode-table start on success or `0` on corruption/error.
