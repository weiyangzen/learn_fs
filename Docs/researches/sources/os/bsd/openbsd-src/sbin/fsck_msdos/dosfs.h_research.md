# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/dosfs.h

## Scope

Core FAT/MS-DOS filesystem data model for `fsck_msdos`.

## Main Types And Constants

- `struct bootblock` stores decoded BPB fields, FAT32 FSInfo/backup fields, calculated geometry, FAT type mask, and scan statistics.
- `struct fatEntry` stores internal per-cluster state: `next`, chain `head`, chain `length`, and flags such as `FAT_USED`.
- `struct dosDirEntry` stores architecture-independent directory tree nodes with parent/next/child links, short name, long name, attributes, start cluster, size, and fsck flags.
- `struct dirTodoNode` is the pending-directory stack node.
- Defines cluster values and masks for FAT12/16/32, LFN sequence bits, directory-empty flags, and `DOSBOOTBLOCKSIZE`.

## Dependencies

Included by `ext.h`, which exposes these types to all `fsck_msdos` modules.

## Risks And Edge Cases

- `NumClusters` is described as FAT entries count but used as the upper cluster bound.
- FAT32 support is folded into `bootblock.flags` and `ClustMask`, so callers must consistently branch on both.
