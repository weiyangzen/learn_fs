# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/mkromfs.c

`mkromfs.c` generates a compressed static data image for Ghostscript's `%rom%` IODevice. It is meant to pack PostScript resources, fonts, and support files into an executable.

The program writes a file named `gsromfs`. For each command-line path, it reads the file, splits it into 4096-byte blocks, compresses each block with zlib `compress`, records compressed lengths, and writes an inode-like record containing next-inode offset, original file length, path length, path bytes, block-size table, and compressed data blocks.

`romfs_inode` stores name, block count, original length, offset, compressed data size, compressed block pointers, and block lengths. `inode_clear` frees allocated inode memory. `inode_write` serializes the inode and logs details to stdout. `put_int32` writes big-endian 32-bit fields.

Risks are significant: the program does not check many allocation or file-open failures, uses `strdup` without validation, computes a per-node offset but does not accumulate the unused `offset` variable, and uses host-endian `fwrite` for `data_lengths` despite big-endian header fields. It is a historical build utility rather than robust archive tooling.
