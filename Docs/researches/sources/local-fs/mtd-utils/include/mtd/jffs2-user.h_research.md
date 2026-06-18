# File Research: sources/local-fs/mtd-utils/include/mtd/jffs2-user.h

## Purpose
User-space endian and xattr helpers for JFFS2 tooling.

## Key Elements
Includes `linux/jffs2.h`, declares external `target_endian`, defines conversion macros for JFFS2 endian-wrapped types, little-endian helpers, xattr namespace strings, JFFS2 ACL structs, and POSIX ACL xattr structs.

## Dependencies
Depends on `endian.h`, `byteswap.h`, and a program-defined `target_endian` global.

## Behavior/Risks
Conversion macros depend on mutable global `target_endian`; tools parsing images must set it correctly for cross-endian images.
