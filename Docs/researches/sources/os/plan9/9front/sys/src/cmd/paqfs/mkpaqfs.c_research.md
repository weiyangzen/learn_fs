# File Research: sources/os/plan9/9front/sys/src/cmd/paqfs/mkpaqfs.c

## Role

Builds a `paqfs` archive from a file or directory tree.

## Archive Construction

`paqfs` writes a header, recursively packs the root as either file or directory, writes the root directory entry block, and appends a trailer.

Files are split into fixed-size data blocks. A pointer block stores 32-bit block offsets. The original file length is preserved in the directory entry, while the final data block is padded to full block size.

Directories are packed recursively. Directory entries are serialized into directory blocks, with a pointer block listing those directory blocks.

## Encoding And Integrity

Each block has a `PaqBlock` header with type, encoded size, encoding, and Adler-32 of unencoded block data. Unless `-u` is used, `writeBlock` attempts deflate compression and stores compressed data only when smaller.

`outWrite` updates a running SHA1 digest over archive bytes. `writeTrailer` stores the root offset and final digest.

## Format Serialization

The file provides big-endian serializers for headers, blocks, trailers, directory entries, integers, shorts, and length-prefixed strings. It supports alternate “big” header/block forms when block size or encoded size exceeds 16-bit limits.

## Options

Supports uncompressed mode, compression level, block size with optional `k` suffix, output path, and label.
