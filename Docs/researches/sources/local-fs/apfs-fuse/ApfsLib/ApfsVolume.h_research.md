# File Research: sources/local-fs/apfs-fuse/ApfsLib/ApfsVolume.h

This header declares `ApfsVolume`, the APFS volume abstraction over an `ApfsContainer`.

Public API includes normal initialization, snapshot mounting, volume name access, diagnostic dumping, references to filesystem and fext B-trees, text-format flags, container access, encrypted-aware block reads, and sealed-volume detection.

Private state includes the copied APFS superblock, volume OMAP, filesystem tree, extent-ref tree, snapshot metadata tree, fext tree, physical address of the APFS superblock, encryption flag, and AES-XTS state.

The class is intentionally read-only. It exposes internal B-tree references because `ApfsDir` directly performs filesystem record lookups.
