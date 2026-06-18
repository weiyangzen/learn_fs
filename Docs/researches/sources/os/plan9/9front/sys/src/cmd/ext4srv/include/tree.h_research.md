# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/tree.h

## Purpose
Provides BSD-style intrusive splay tree and red-black tree macro generators for `ext4srv`.

## Key Elements
Defines `SPLAY_HEAD`, `SPLAY_ENTRY`, splay rotations, generated insert/remove/find/next/min/max functions, and `SPLAY_FOREACH`. Defines `RB_HEAD`, `RB_ENTRY`, color/parent accessors, rotations, generated insert/remove/color-fix/find/nearest-find/next/prev/min/max functions, and forward/reverse traversal macros.

## Dependencies
Macro-only header using caller-provided comparison functions and embedded node fields. It expects Plan 9 `nil` and supports optional `RB_AUGMENT` callbacks for augmented tree metadata.

## Behavior/Risks
Generated code performs structural mutation during splay lookups and assumes comparator consistency. RB remove/color code requires valid parent/color fields; misuse can corrupt the tree silently. There is no locking or validation layer in this header.
