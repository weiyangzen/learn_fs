# File Research: sources/windows/windows-driver-samples/filesys/fastfat/lfn.h

## Purpose

`lfn.h` defines the on-disk FAT long-file-name dirent format and related constants. It is a compact wire-format header used by FastFAT name parsing and directory-entry code.

## Main Contents

- `PACKED_LFN_DIRENT`
  - 32-byte on-disk long-name directory entry.
  - Fields:
    - `Ordinal`
    - `Name1[10]` for five unaligned UTF-16 characters
    - `Attributes`
    - `Type`
    - `Checksum`
    - `Name2[6]`
    - `MustBeZero`
    - `Name3[2]`
  - Represents 13 UTF-16 code units per LFN dirent, split around metadata fields.

- Pointer/type aliases:
  - `PPACKED_LFN_DIRENT`
  - `LFN_DIRENT`
  - `PLFN_DIRENT`

- Constants:
  - `FAT_LAST_LONG_ENTRY` marks the final ordinal entry in an LFN sequence.
  - `FAT_LONG_NAME_COMP` is the expected component type.
  - `MAX_LFN_CHARACTERS` is 260.
  - `MAX_LFN_DIRENTS` is 20.

- Macro:
  - `FAT_LFN_DIRENTS_NEEDED(NAME)` computes the number of 13-character LFN dirents needed for a counted Unicode name.

## Integration Points

The structure mirrors FAT’s packed directory-entry layout and is consumed by name-support and directory-scanning logic. The split `Name1` byte array avoids assuming WCHAR alignment for the first five characters.

## Risk Notes

- The file defines packed on-disk layout, so consumers must respect unaligned fields.
- The dirent-count macro assumes `NAME->Length` is in bytes and divides by `sizeof(WCHAR)`.
