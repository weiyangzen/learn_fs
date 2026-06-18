# File Research: sources/windows/reactos/drivers/filesystems/fastfat/lfn.h

## Scope

This header defines the on-disk FAT long-file-name directory-entry layout and small constants/macros used to size LFN storage.

## APIs And Constants

- `PACKED_LFN_DIRENT` models a 32-byte FAT LFN dirent:
  - `Ordinal` at offset 0.
  - `Name1[10]` at offset 1, representing five UTF-16 characters stored byte-packed because the field is not WCHAR-aligned.
  - `Attributes` at offset 11.
  - `Type` at offset 12.
  - `Checksum` at offset 13.
  - `Name2[6]` at offset 14.
  - `MustBeZero` at offset 26.
  - `Name3[2]` at offset 28.
- Pointer aliases: `PPACKED_LFN_DIRENT`, `LFN_DIRENT`, and `PLFN_DIRENT`.
- LFN markers: `FAT_LAST_LONG_ENTRY` for the ordinal high bit and `FAT_LONG_NAME_COMP` for the type field.
- Limits: `MAX_LFN_CHARACTERS` is 260 and `MAX_LFN_DIRENTS` is 20.
- `FAT_LFN_DIRENTS_NEEDED(NAME)` computes the number of 13-character LFN entries needed for a Unicode string length.

## Role

- Provides the packed ABI contract between directory parsing code and FAT on-disk LFN entries.
- Documents that a packed LFN dirent is already quadword aligned, so the normal LFN dirent typedef is the packed type.

## Dependencies

- Relies on Windows-style integer and character typedefs such as `UCHAR`, `USHORT`, and `WCHAR`.
- Included by fastfat directory/name parsing code that needs to recognize or emit long-name dirent chains.

## Risks And Invariants

- Field offsets and total size must remain exactly aligned with the FAT on-disk format. Padding changes would corrupt parsing.
- `Name1` is intentionally byte-addressed rather than `WCHAR[5]`; consumers must account for its unaligned packed representation.
- The dirent-count macro assumes 13 UTF-16 code units per LFN entry and a byte-length `UNICODE_STRING`-style `Length`.
