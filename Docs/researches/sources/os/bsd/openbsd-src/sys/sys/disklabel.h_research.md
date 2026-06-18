# File Research: sources/os/bsd/openbsd-src/sys/sys/disklabel.h

This header defines OpenBSD disklabel, partition, GPT, and DOS MBR layout constants and helpers.

Key definitions:
- Paths and constants: `_PATH_DISKTAB`, `DISKTAB`, `MAXPARTITIONSUNIT`, `MAXPARTITIONS16`, `RAW_PART`, `DISKMAGIC`, `MAXDISKSIZE`.
- Device translation macros: `DISKUNIT`, `DISKPART`, `DISKMINOR`, `MAKEDISKDEV`, `DISKLABELDEV`.
- `struct disklabel` with geometry, UID, 48-bit size/start/end high parts, checksum, partition count, and `d_partitions[MAXPARTITIONSUNIT]`.
- Partition helpers: `DL_GETPSIZE`, `DL_SETPSIZE`, `DL_GETPOFFSET`, `DL_SETPOFFSET`, `DL_GETDSIZE`, `DL_SETDSIZE`, `DL_GETBSTART`, `DL_SETBSTART`, `DL_GETBEND`, `DL_SETBEND`.
- Block/sector conversion helpers and partition name/number inline functions.
- Disk and filesystem type constants, plus optional name tables under `DKTYPENAMES`.
- GPT structures/constants and OpenBSD/EFI GUID constants.
- DOS MBR structures/constants and known DOS partition types.

Kernel APIs:
- Disklabel operations: `diskerr`, `dkcksum`, `initdisklabel`, `checkdisklabel`, `setdisklabel`, `readdisklabel`, `writedisklabel`, `bounds_check_with_label`, `readdisksector`, `readdoslabel`.
- Optional spoofers for `CD9660` and `UDF`.
- Userland: `getdiskbyname`.

Risk notes:
- 48-bit disk-size fields are split high/low; direct field access can truncate sizes.
- GPT fields are specified little-endian by UEFI even on big-endian systems.
- `DOS_LABELSECTOR` and machine-dependent `<machine/disklabel.h>` make label placement platform-sensitive.
