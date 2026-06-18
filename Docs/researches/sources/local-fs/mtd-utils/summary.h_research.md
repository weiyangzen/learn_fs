# File Research: sources/local-fs/mtd-utils/summary.h

## Purpose
Defines JFFS2 summary record structures and accounting helpers for `sumtool`.

## Key Elements
Provides space accounting macros, block state constants, summary record size macros, packed on-flash summary structures for inode/dirent/xattr/xref records, in-memory linked-list variants, `struct jffs2_summary`, summary marker layout, and summary frame sizing.

## Dependencies
Includes `linux/jffs2.h` for JFFS2 node types and integer wrappers.

## Behavior/Risks
The packed structures must match JFFS2 summary media format exactly. The accounting macros assume caller variables named `c` and `jeb`, making them kernel-style contextual macros rather than standalone helpers.
