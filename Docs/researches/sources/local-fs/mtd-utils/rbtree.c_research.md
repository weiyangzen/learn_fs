# File Research: sources/local-fs/mtd-utils/rbtree.c

## Purpose
User-space copy of the Linux intrusive red-black tree implementation.

## Key Elements
Implements left/right rotations, insertion rebalancing, deletion rebalancing, erase, first/last, next/previous traversal, and node replacement.

## Dependencies
Depends on `rbtree.h` for node layout, parent/color packing macros, and exported prototypes.

## Behavior/Risks
Provides only structural tree operations; callers must implement their own ordered insert/search logic and maintain key uniqueness rules. It assumes embedded `rb_node` ownership, Linux-style container macros, and correct caller linkage.
