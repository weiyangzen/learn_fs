# File Research: sources/local-fs/e2fsprogs/e2fsck/extend.c

## Purpose
Small standalone helper that extends a file to at least a requested number of blocks by reading and rewriting the final target block.

## Main Behavior
- CLI: `extend filename nblocks blocksize`.
- Allocates a zeroed block buffer.
- Opens file read/write.
- Seeks to `(nblocks - 1) * blocksize`, reads a block, seeks back, and writes a block.

## Integration
Built as optional helper target `extend` in `Makefile.in`, not part of the main `e2fsck` binary.

## Risks / Notes
Uses `int` for seek offset result and block arithmetic, so it is not suitable for very large offsets on all platforms. Error message after failed write says `"read"`, likely a copy/paste typo.
