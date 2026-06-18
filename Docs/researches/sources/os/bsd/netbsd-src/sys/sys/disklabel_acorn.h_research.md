# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel_acorn.h

Defines Acorn FileCore and RISCiX partition structures and helpers for disklabel integration.

Key content:
- Partition type/format constants for unused, ADFS, RISCiX, and RISCBSD.
- FileCore boot sector location.
- RISCiX partition table constants and structures.
- `struct filecore_bootblock` with geometry, root, disk size/id/name/type, partition cylinder range, and checksum.
- Kernel prototypes: `filecore_label_read` and `filecore_label_locate`.

Important behavior:
- Kernel helpers are guarded by `_KERNEL` and not assembler.
- Used by disklabel read/write paths to recognize Acorn partitioning.
