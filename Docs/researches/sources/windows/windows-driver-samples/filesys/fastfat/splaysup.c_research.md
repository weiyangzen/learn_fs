# File Research: sources/windows/windows-driver-samples/filesys/fastfat/splaysup.c

## Purpose
Implements name lookup support using RTL splay trees. It inserts, removes, finds, and compares FAT file-name nodes used by DCB directory children.

## Main Entry Points
- `FatInsertName`: inserts a `FILE_NAME_NODE` into an OEM-name splay tree.
- `FatRemoveNames`: removes an FCB’s short and long names from parent DCB splay trees.
- `FatFindFcb`: searches a splay tree by name and splays the found node to root.
- `FatCompareNames`: deterministic bytewise name comparison.

## Behavior
`FatInsertName` initializes the new node’s splay links and walks the current root comparing OEM names with `CompareNames`. It inserts as a left child when the existing node is greater, otherwise as a right child. If an equal name already exists, it treats this as serious unless the existing FCB is no longer good. For stale duplicate names, it marks the old FCB bad, removes its names, and restarts insertion so the new name wins.

`FatRemoveNames` removes the FCB short name from the parent’s OEM splay tree. If OEM long-name and Unicode long-name nodes are present, it removes those from the appropriate parent roots, frees their allocated string buffers, clears state flags, and finally clears `FCB_STATE_NAMES_IN_SPLAY_TREE`.

`FatFindFcb` searches the tree with `CompareNames`. On a match, it splays the matching node to the root, optionally returns whether the matched node represents a DOS filename, and returns the node’s FCB. Missing names return `NULL`.

`FatCompareNames` compares two counted byte strings by `RtlCompareMemory`, then length. It is intentionally case-sensitive and byte-oriented; comments note that whether the bytes represent OEM or Unicode does not matter for deterministic tree ordering.

## Data Structures
- `PRTL_SPLAY_LINKS`: tree links.
- `FILE_NAME_NODE`: contains splay links, name, FCB pointer, and DOS-name marker.
- Parent DCB roots:
  - `Parent->Specific.Dcb.RootOemNode`
  - `Parent->Specific.Dcb.RootUnicodeNode`

## Dependencies
- `RtlInitializeSplayLinks`
- `RtlInsertAsLeftChild`
- `RtlInsertAsRightChild`
- `RtlDelete`
- `RtlSplay`
- `RtlLeftChild`
- `RtlRightChild`
- `RtlFreeOemString`
- `RtlFreeUnicodeString`
- `FatMarkFcbCondition`
- `FatBugCheck`

## Important Notes
This file maintains the in-memory directory-name index. Correct removal of all short/OEM-long/Unicode-long nodes is essential before rename, teardown, or stale-media recovery. Duplicate-name handling explicitly accounts for removable media changing underneath still-open handles.
