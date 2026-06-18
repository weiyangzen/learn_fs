# File Research: sources/os/plan9/plan9/sys/src/cmd/paqfs/paqfs.h

Shared on-disk format definitions for `mkpaqfs` and `paqfs`.

Defines header, block, trailer, and directory structures plus magic numbers, version, fixed header sizes, min/max block sizes, block types, and encodings.

`PaqHeader` records archive metadata. `PaqBlock` describes each stored block’s encoded size, semantic type, encoding, and Adler-32 checksum. `PaqTrailer` records the root directory block offset and final SHA1 digest. `PaqDir` is the serialized directory/file metadata model used by both writer and reader.
