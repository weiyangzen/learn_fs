# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/bpb.h

Defines BIOS Parameter Block and FAT32 FSInfo layouts for msdosfs.

Main responsibilities:
- Provides native BPB structs for DOS 3.3, DOS 5.0, and DOS 7.10/FAT32.
- Provides byte-packed on-disk BPB structs that avoid compiler alignment assumptions.
- Defines little-endian load/store macros for BPB fields.
- Defines FAT32 flags/version/root/info/backup boot-sector fields and FSInfo block layout.

Key structures and constants:
- `struct bpb33`, `bpb50`, `bpb710`: typed in-memory BPB layouts.
- `struct byte_bpb33`, `byte_bpb50`, `byte_bpb710`: byte-array disk layouts.
- `FATNUM`, `FATMIRROR`, and `FSVERS` describe FAT32 extended flags/version behavior.
- `struct fsinfo` contains FAT32 FSInfo signatures, free-cluster count, and next-free hint.
- `getushort`, `getulong`, `putushort`, `putulong` wrap little-endian decoding/encoding.

Important dependencies:
- Uses `<sys/endian.h>` little-endian helpers.
- Consumed by mount, FAT, directory, and conversion code that parses or writes FAT metadata.

Notable risks and edge cases:
- Disk fields are little-endian and often unaligned; callers must use the byte-layout structures and endian macros for on-disk data.
- FAT32 support depends on correctly interpreting `bpbBigFATsecs`, root cluster, FSInfo sector, and mirroring flags.
