# File Research: sources/local-fs/mtd-utils/sumtool.c

## Purpose
Converts a JFFS2 image into a summarized JFFS2 image to speed mounts on kernels with summary support.

## Key Elements
Parses input/output, eraseblock size, endianness, cleanmarker behavior, and final padding. Reads input eraseblocks, scans JFFS2 nodes, validates header/node/data/name CRCs, copies recognized inode/dirent/xattr/xref nodes into an output eraseblock buffer, collects summary entries, emits summary nodes and end markers, handles cleanmarkers, pads as needed, and writes output buffers.

## Dependencies
Uses `summary.h`, `mtd/jffs2-user.h`, `crc32`, endian conversion macros, POSIX I/O, and `common.h`.

## Behavior/Risks
Malformed nodes are skipped with warnings, so output may omit corrupted data rather than preserving it byte-for-byte. The tool operates in eraseblock-sized buffers and assumes enough room for summary metadata when deciding to flush. It mutates node accuracy bits in the in-memory input buffer while processing.
