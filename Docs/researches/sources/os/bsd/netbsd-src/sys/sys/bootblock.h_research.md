# File Research: sources/os/bsd/netbsd-src/sys/sys/bootblock.h

## Scope

Defines on-disk boot block, partition, boot-parameter, and platform-specific boot metadata layouts used by NetBSD installboot, disklabel, and boot code.

## APIs And Data Structures

- MBR constants define sector offsets, magic values, boot selector layout, partition table offsets, GPT protective MBR details, partition flags, and a large catalog of MBR partition type IDs.
- Optional `MBRPTYPENAMES` emits a partition type/name lookup table.
- Provides `MBR_PSECT`, `MBR_PCYL`, and `MBR_IS_EXTENDED`.
- Defines packed FAT12/FAT16/FAT32 BIOS parameter blocks, `mbr_bootsel`, `mbr_partition`, and full `mbr_sector`.
- Declares `xlat_mbr_fstype(int)`.
- Defines `shared_bbinfo` block-location metadata.
- Defines platform records for Alpha boot blocks with checksum macro, Apple driver/partition maps and A/UX block zero data, HP300/HPPA LIF volumes/directories, x86 and landisk boot params, next68k disklabels, pmax boot maps, SGI volume headers, VAX boot blocks, and magic/offset/size constants for ews4800mips, macppc, news, sparc, sparc64, sun68k, x68k.

## Behavior

- Structures mirror disk bytes and are mostly packed.
- Alpha checksum sums little-endian 64-bit data words and writes a little-endian checksum.
- x86 boot params include timeout, console settings, password hash, keyboard map, and flags for video reset, password, modules, bootconf, and LBA64 validity.

## Dependencies

- Includes `sys/cdefs.h`, `sys/endian.h`, and integer headers outside assembler.

## Risks And Invariants

- This is disk ABI; offsets, packing, endian conversions, and magic values must remain exact.
- Several definitions are shared with assembler and boot code, so preprocessor guards matter.
- Some platform formats encode historical firmware quirks and fixed sector sizes.
