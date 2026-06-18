# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/mkromfs.c

## Purpose
Utility that compresses files into a binary `gsromfs` image for Ghostscript’s `%rom%` IODevice.

## Main Structure
- Defines ROM filesystem block size as 4096 bytes and computes zlib compression buffer size.
- `romfs_inode` stores file name, length, compressed block count, data arrays, and metadata.
- `put_int32` writes big-endian 32-bit values.
- `inode_clear` frees per-inode memory.
- `inode_write` writes inode header, path, block-size table, and compressed blocks.
- `main` opens `gsromfs`, iterates input file paths, compresses each file block-by-block with zlib, writes records, and frees buffers.

## Output Format Signals
- Per file: next-inode offset, original length, path length, path bytes, compressed block lengths, compressed data.
- Logs compression and write details to stdout.

## Risks and Edge Cases
- No error checking for `malloc`, `calloc`, `fopen`, `fseek`, `ftell`, `fread`, or output file creation.
- Division by zero if an input file has length 0 when printing compression percentage.
- Local `offset` in `main` is unused.
- `node->offset` is computed as per-record size, not accumulated global file offset; reader expectations must match that design.
- `cbuf` is not freed before exit, though process teardown reclaims it.
