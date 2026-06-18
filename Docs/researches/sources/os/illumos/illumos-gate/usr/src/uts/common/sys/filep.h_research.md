# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/filep.h

Defines private standalone/boot-style file and device identification structures tied to UFS headers. `devid_t` stores a description, device cookie, taken flag, and an embedded UFS superblock-sized union.

`fileid_t` stores a file descriptor id, path, block number, count, offset, memory pointer, taken flag, cache/compression flags, owning device id, block buffer, block-read callback, UFS inode pointer, list links, compressed-file offset, decompression scratch buffer metadata, and zlib stream pointer.

Flags include cached/partial/no-cache bits borrowed from inode flags plus `FI_COMPRESSED` and `DECOMP_BUFSIZE`. It declares `diskread(fileid_t *)`.
