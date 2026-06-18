# File Research: sources/os/bsd/dragonflybsd/sys/sys/disklabel.h

Abstract disklabel dispatch layer for 32-bit and 64-bit DragonFly disk labels.

Key responsibilities:
- Defines `disklabel_t` union wrapping opaque, `disklabel32 *`, or `disklabel64 *`.
- Defines maximum pack name length.
- Defines `struct disklabel_ops`, including label type UUID, on-disk label size, and operations to read, set, write, clone, adjust reserved areas, get partition bounds, load partinfo, get partition count, get pack name, make a virgin label, and free labels.
- Provides typedef `disklabel_ops_t`.

Dependencies:
- Includes `sys/types.h` and `sys/uuid.h`.
- Forward-declares cdev, diskslice(s), disk_info, and partinfo.

Notable risks:
- This abstraction lets disk slice code handle multiple on-disk label formats; every op must agree on units and reserved-region semantics.
- `disklabel_t` is a tagged-by-context union with no runtime discriminator.
