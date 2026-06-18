# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fat.h

## Purpose

`fat.h` defines FastFAT’s on-disk FAT structures, constants, and low-level macros. It covers BIOS Parameter Blocks, boot sectors, FAT entries, directory entries, timestamp layout, FAT geometry conversion, FAT12 entry packing, and the on-disk EA file format.

## Addressing Types

- `LBO` is a signed 64-bit logical byte offset for disk-relative byte positions.
- `VBO` is a 32-bit virtual byte offset for file/directory/allocation-relative positions.

## Boot Sector and BPB Definitions

The header defines packed and unpacked BIOS Parameter Block forms:

- `PACKED_BIOS_PARAMETER_BLOCK`
- `PACKED_BIOS_PARAMETER_BLOCK_EX` for FAT32
- `BIOS_PARAMETER_BLOCK`

Important helpers:

- `IsBpbFat32(bpb)` checks whether `SectorsPerFat` is zero.
- `FatUnpackBios(Bios, Pbios)` copies packed unaligned byte fields into an unpacked BPB.
- `PACKED_BOOT_SECTOR` and `PACKED_BOOT_SECTOR_EX` model FAT12/16 and FAT32 boot sectors.
- `FSINFO_SECTOR` models the FAT32 FSInfo sector.

## FAT and Dirty-State Constants

The file defines FAT entry values and masks:

- `FAT_ENTRY` as `ULONG32`
- `FAT32_ENTRY_MASK`
- `FAT_CLUSTER_AVAILABLE`
- `FAT_CLUSTER_RESERVED`
- `FAT_CLUSTER_BAD`
- `FAT_CLUSTER_LAST`
- clean/dirty marker constants for FAT12/FAT16/FAT32

It also defines boot-sector dirty flags:

- `FAT_BOOT_SECTOR_DIRTY`
- `FAT_BOOT_SECTOR_TEST_SURFACE`

## Time and Directory Structures

- `FAT_TIME`, `FAT_DATE`, and `FAT_TIME_STAMP` model FAT’s packed timestamp format.
- `FAT8DOT3` models the 11-byte short name.
- `PACKED_DIRENT` / `DIRENT` models a 32-byte FAT directory entry, including:
  - 8.3 name
  - attributes
  - NT byte
  - creation/write/access timestamps
  - high cluster word or EA handle
  - first cluster low word
  - file size

Dirent markers and attributes include:

- never-used, deleted, alias, and escaped `0xE5`
- read-only, hidden, system, volume ID, directory, archive, device
- LFN attribute combination
- NT byte flags for encrypted/EFS and lowercase name optimization

## Geometry Macros

The header provides macro calculations for FAT volume layout:

- `FatBytesPerCluster`
- `FatBytesPerFat`
- `FatReservedBytes`
- `FatRootDirectorySize`
- `FatRootDirectoryLbo`
- `FatRootDirectoryLbo32`
- `FatFileAreaLbo`
- `FatNumberOfClusters`
- `FatIndexBitSize`
- `FatGetLboFromIndex`
- `FatGetIndexFromLbo`

`FatVerifyIndexIsValid` raises `STATUS_FILE_CORRUPT_ERROR` if a cluster index is outside valid volume bounds.

## FAT12 Entry Helpers

- `FatLookup12BitEntry` reads a 12-bit FAT entry from packed FAT12 storage.
- `FatSet12BitEntry` updates a packed 12-bit FAT entry while preserving neighboring nibble data.

These macros rely on unaligned byte-copy helpers to avoid alignment faults.

## EA On-Disk Format

The file defines FAT EA metadata structures:

- `EA_FILE_HEADER`
  - signature
  - recovery/log fields
  - base table of 240 entries
- `EA_OFF_TABLE`
  - 128 offset entries
- `EA_SET_HEADER`
  - per-file EA set signature
  - owner handle
  - `NeedEaCount`
  - owner short filename
  - packed `cbList`
  - packed EA payload
- `PACKED_EA`
  - flags
  - name length
  - value length
  - null-terminated name followed by value

EA constants include:

- `EA_FILE_SIGNATURE`
- `EA_SET_SIGNATURE`
- `SIZE_OF_EA_SET_HEADER`
- `MAXIMUM_EA_SIZE`
- `EA_NEED_EA_FLAG`
- `MIN_EA_HANDLE`
- `MAX_EA_HANDLE`
- `UNUSED_EA_HANDLE`
- table-size constants

Helpers:

- `GetcbList` and `SetcbList` manipulate the packed 4-byte `cbList`.
- `GetEaValueLength` and `SetEaValueLength` manipulate packed value length.
- `SizeOfPackedEa` computes packed EA record size.

## Integration

`fat.h` is foundational for the EA implementation in `easup.c`, the dirent/cluster logic used throughout FastFAT, and BPB/volume layout code elsewhere in the driver.
