# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fat.h

This header defines FastFAT’s on-disk format contracts and core layout macros: boot sectors, BPBs, FAT entries, timestamps, directory entries, FAT geometry calculations, FAT12 entry packing, and extended-attribute structures.

Major definitions:
- Basic offset types:
  - `LBO` is a signed 64-bit logical byte offset, needed for FAT32-scale media.
  - `VBO` is a 32-bit file-relative byte offset.
- Packed BPB structures:
  - `PACKED_BIOS_PARAMETER_BLOCK` for FAT12/16-style BPB fields.
  - `PACKED_BIOS_PARAMETER_BLOCK_EX` for FAT32 extensions.
  - `BIOS_PARAMETER_BLOCK` is the unpacked in-memory form.
  - `FatUnpackBios` copies unaligned packed fields into the unpacked structure.
  - `IsBpbFat32` detects FAT32 by zero `SectorsPerFat`.
- Boot sector structures:
  - `PACKED_BOOT_SECTOR`
  - `PACKED_BOOT_SECTOR_EX`
  - `FSINFO_SECTOR` and FAT32 FSInfo signatures.
- FAT state:
  - `FAT_ENTRY`
  - FAT32 entry mask and clean/dirty constants.
  - available/reserved/bad/last-cluster markers.
- Time and directory layout:
  - `FAT_TIME`, `FAT_DATE`, `FAT_TIME_STAMP`.
  - `FAT8DOT3`.
  - `PACKED_DIRENT`/`DIRENT`, a 32-byte on-disk directory entry with attributes, timestamps, cluster fields, and file size.
  - Dirent first-byte states and attributes, including LFN attribute composition.
  - NT byte flags for EFS and lowercase-name optimization.
- Geometry macros:
  - `FatBytesPerCluster`
  - `FatBytesPerFat`
  - `FatReservedBytes`
  - `FatRootDirectorySize`
  - `FatRootDirectoryLbo`
  - `FatRootDirectoryLbo32`
  - `FatFileAreaLbo`
  - `FatNumberOfClusters`
  - `FatIndexBitSize`
- Allocation translation:
  - `FatVerifyIndexIsValid`
  - `FatGetLboFromIndex`
  - `FatGetIndexFromLbo`
- FAT12 helpers:
  - `FatLookup12BitEntry`
  - `FatSet12BitEntry`
- EA structures:
  - `EA_FILE_HEADER` for the hidden EA file header.
  - `EA_OFF_TABLE` for handle offset tables.
  - `EA_SET_HEADER` for a per-file EA set.
  - `PACKED_EA` for individual packed EAs.
  - `GetcbList`, `SetcbList`, `GetEaValueLength`, `SetEaValueLength`, and `SizeOfPackedEa`.
  - EA limits such as `MAXIMUM_EA_SIZE`, `MIN_EA_HANDLE`, `MAX_EA_HANDLE`, `UNUSED_EA_HANDLE`, `MAX_EA_BASE_INDEX`, and `MAX_EA_OFFSET_INDEX`.

Important filesystem semantics:
- FAT32 root directory handling differs from FAT12/16: the root is cluster-chain backed, while FAT12/16 has a fixed root directory region.
- Cluster indexes 0 and 1 are invalid for normal data; valid file clusters begin at 2.
- FAT type selection is cluster-count based for non-FAT32 volumes.
- FAT12 entries are 12-bit packed entries shared across byte boundaries, requiring unaligned copy/shifting helpers.
- EA constants and structures are consumed directly by `easup.c`.

Role in the subset:
- This is the central on-disk FAT schema file for the FastFAT sample. It maps raw FAT bytes into C structures and provides the arithmetic used by mount, allocation, directory, and EA code.
