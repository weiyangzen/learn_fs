# File Research: sources/os/bsd/dragonflybsd/sys/sys/diskmbr.h

Legacy MBR partition table constants, type names, and partition entry format.

Key responsibilities:
- Defines MBR sector offsets, partition entry size/count, extended partition constants, boot signature offset/value, and many partition type IDs.
- Defines DragonFly BSD partition type `0x6C`, with comment noting previous use of `0xA5` and GRUB conflicts.
- Provides a static partition type-to-name table when not standalone.
- Defines packed logical `struct dos_partition` fields for CHS start/end, type, LBA start, and sector count.
- Uses compile-time assertion to ensure entry size is 16 bytes.
- Provides CHS sector/cylinder extraction macros.

Dependencies:
- Includes `sys/types.h`; defines fallback `CTASSERT` if absent.

Notable risks:
- CHS sector numbers are one-based in MBR, while block I/O is zero-based.
- The static name table in a header can create per-translation-unit copies.
