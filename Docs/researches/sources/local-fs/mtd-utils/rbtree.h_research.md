# File Research: sources/local-fs/mtd-utils/rbtree.h

## Purpose
Header for the intrusive red-black tree helper.

## Key Elements
Defines `struct rb_node`, `struct rb_root`, packed parent/color macros, `RB_ROOT`, container helpers, empty-node helpers, exported tree operations, and `rb_link_node()`.

## Dependencies
Includes Linux-style `kernel.h` and `stddef.h`.

## Behavior/Risks
The parent pointer and color share low pointer bits, so node alignment is required. This is a low-level utility with no comparison callbacks; misuse by callers can silently corrupt tree ordering.
