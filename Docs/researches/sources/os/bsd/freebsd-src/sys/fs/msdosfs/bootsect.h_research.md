# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bootsect.h

Defines on-disk boot-sector layouts for FAT/MS-DOS filesystems.

Main responsibilities:
- Describes DOS 3.3, DOS 5.0, and DOS 7.10/FAT32 boot sectors as fixed 512-byte structures.
- Defines the extended boot record fields used by FAT12/FAT16 volume metadata.
- Provides boot-sector signature constants `BOOTSIG0` and `BOOTSIG1`, and extended signature `EXBOOTSIG`.

Key structures:
- `struct bootsector33`: 3-byte jump, OEM name, 19-byte BPB, drive number, boot code pad, signature.
- `struct extboot`: drive number, reserved byte, extended signature, volume ID, label, filesystem type.
- `struct bootsector50`: DOS 5.0 boot sector with 25-byte BPB and 26-byte extension.
- `struct bootsector710`: FAT32 boot sector with 53-byte BPB and 26-byte extension.
- `union bootsector`: overlays all supported boot-sector forms.

Important dependencies:
- Paired with `bpb.h`, which defines the BIOS Parameter Block layouts embedded in these boot-sector byte arrays.

Notable risks and edge cases:
- These are disk-format structures; fields are byte arrays where alignment/endian handling is expected elsewhere.
- A disabled `#if 0` shorthand block documents older BPB field aliases but is not active.
