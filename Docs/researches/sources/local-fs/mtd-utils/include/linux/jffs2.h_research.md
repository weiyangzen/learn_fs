# File Research: sources/local-fs/mtd-utils/include/linux/jffs2.h

## Purpose
User-space copy of JFFS2 on-flash constants and node layout definitions.

## Key Elements
Defines JFFS2 magic values, compression IDs, compatibility flags, node types, xattr prefixes, endian wrapper structs, raw inode/dirent/xattr/xref/summary structs, and `union jffs2_node_union`.

## Dependencies
Requires C99 fixed-width integer types to be included before use.

## Behavior/Risks
All raw structs are packed and model physical media layout. Any changes must remain ABI-compatible with kernel JFFS2 format.
