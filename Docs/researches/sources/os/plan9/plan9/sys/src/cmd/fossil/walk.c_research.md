# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/walk.c

This file implements generic traversal over Fossil blocks. `initWalk` initializes a `WalkPtr` for data, directory-entry, or pointer blocks, while `nextWalk` emits the next child score/type/tag and optionally an unpacked `Entry`.

For directory blocks, iteration returns active entry-derived targets using entry type (`BtDir` or `BtData` plus depth). For pointer blocks, it returns child scores with decremented block type and inherited tag. `BtData` has no children.

It is a small reusable walker for archive/check/traversal code.
