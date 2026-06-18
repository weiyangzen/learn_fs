# File Research: sources/local-fs/mtd-utils/jffs2reader.c

## Purpose
Reads JFFS2 images to list directories recursively or extract a regular file to stdout.

## Key Elements
Loads the whole image, reconstructs files and directories by scanning nodes in version order, supports zlib/none/zero compression, resolves absolute and relative paths including `.`/`..` and symlinks, prints ls-like metadata, and extracts selected files using a 5 MiB scratch buffer.

## Dependencies
Uses zlib, `mtd/jffs2-user.h`, and `common.h` allocation/error helpers.

## Behavior/Risks
The file documents that CRC checking is missing. It does not support all JFFS2 compression methods, uses fixed buffers for names/symlinks/scratch extraction, and trusts many image lengths after only basic magic scanning.
