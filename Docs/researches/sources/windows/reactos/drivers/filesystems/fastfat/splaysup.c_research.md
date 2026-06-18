# File Research: sources/windows/reactos/drivers/filesystems/fastfat/splaysup.c

This file implements FastFAT’s in-memory filename splay-tree support for cached FCB lookup.

Key responsibilities:
- Insert short and long name nodes into per-directory splay trees.
- Remove all name nodes associated with an FCB.
- Find an FCB by OEM or Unicode name tree lookup and splay the found node to the root.
- Compare name byte strings deterministically.

Important functions:
- `FatInsertName`: inserts a `FILE_NAME_NODE` into a splay tree rooted at a parent DCB field.
- `FatRemoveNames`: removes the short name and any OEM/Unicode long names from the parent DCB’s trees, freeing allocated long-name strings.
- `FatFindFcb`: searches a name tree, splays a match to root, and optionally reports whether the matched node was a DOS/short-name entry.
- `FatCompareNames`: case-sensitive byte comparison used for both OEM and Unicode tree ordering.

Important interactions:
- Parent DCBs maintain separate roots for OEM and Unicode name trees.
- `FatConstructNamesInFcb` inserts names through this file, while deletion/rename paths remove them through `FatRemoveNames`.
- `FatFindFcb` updates `*RootNode` with `RtlSplay(Links)` to improve locality for repeated lookups.

Notable behavior and risks:
- Duplicate insertion normally bugchecks, but the code handles stale bad FCBs caused by removable-media changes: it marks the old FCB bad, removes its names, and restarts insertion.
- `FatRemoveNames` tolerates FCBs that no longer have tree entries, because rename and stale-branch cleanup can revisit partially torn-down children.
- `FatCompareNames` is byte-order deterministic rather than locale-aware; callers must supply appropriately normalized names.
