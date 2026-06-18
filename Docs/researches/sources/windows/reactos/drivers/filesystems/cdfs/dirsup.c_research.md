# File Research: sources/windows/reactos/drivers/filesystems/cdfs/dirsup.c

## Purpose

`dirsup.c` implements CDFS directory-entry support. It maps ISO/HSG directory sectors, validates raw dirent boundaries, converts raw on-disk dirents into in-memory `DIRENT` structures, builds Unicode names, searches for files/directories, handles generated 8.3 aliases, and gathers multi-extent file metadata.

The file documents key ISO9660 directory behavior: dirents are sector-contained, zero padding may fill sector tails, like-named versioned files are contiguous and ordered by decreasing version, and a logical file can span multiple dirents/extents.

## Main Entry Points

- `CdLookupDirent`: starts a directory walk at a known dirent offset. It maps the containing sector with `CcMapData`, initializes `DIRENT_ENUM_CONTEXT`, truncates mapped length at EOF, and validates the raw dirent with `CdCheckRawDirentBounds`.
- `CdLookupNextDirent`: advances to the next valid dirent, possibly unpinning and mapping the next sector. It skips zero-length sector padding and all-zero sectors allowed by CDFS, then validates the found entry.
- `CdUpdateDirentFromRawDirent`: copies unaligned on-disk `RAW_DIRENT` fields into a normalized `DIRENT`, including file location, data length, timestamp pointer, dirent flags, interleave metadata, filename pointer/length, system-use offset, and default XA metadata.
- `CdUpdateDirentName`: converts raw on-disk file identifiers into `CD_NAME` values. It handles `.` and `..` constant entries, OEM-to-Unicode conversion for non-Joliet media, big-endian Unicode conversion for Joliet, filename/version splitting, trailing-dot trimming, legal-name validation, and optional upcase buffers.
- `CdFindFile`: scans a directory for a non-directory, non-associated file matching a `CD_NAME`; if the exact long name fails, it can match a generated short name keyed by dirent offset.
- `CdFindDirectory`: scans only directory entries and matches names without short-name fallback.
- `CdFindFileByShortName`: directly seeks the long file whose generated 8.3 name corresponds to the caller-provided short-name dirent-offset encoding.
- `CdLookupNextInitialFileDirent`: moves from one file’s first dirent to the next file’s first dirent, skipping remaining extents of the prior file when necessary.
- `CdLookupLastFileDirent`: gathers all dirents/extents for a file and computes aggregate file size, including CD-XA mode handling.
- `CdCleanupFileContext`: releases all mapped dirent contexts and allocated dirent name buffers in a `FILE_ENUM_CONTEXT`.
- `CdCheckRawDirentBounds`: validates raw dirent size, minimum length, file identifier capacity, and sector containment; returns the offset to the next dirent or zero for next-sector movement.
- `CdCheckForXAExtent`: parses the XA system-use area, recognizes XA signatures, audio extents, and Mode2 Form2 data, and stores XA attributes/file number.

## Data Flow

Directory walking centers on `DIRENT_ENUM_CONTEXT`, which stores the mapped sector, sector base offset, current offset, data length, BCB, and next-dirent offset. `COMPOUND_DIRENT` pairs this context with the normalized `DIRENT`. `FILE_ENUM_CONTEXT` keeps prior, initial, and current compound dirents so callers can scan files that may contain multiple extents.

Raw dirent lookup proceeds as:

1. Map a sector from the directory stream file.
2. Use the `CdRawDirent` macro to address the raw dirent at `Sector + SectorOffset`.
3. Validate bounds and derive the next offset.
4. Copy raw metadata into `DIRENT`.
5. Convert raw file ID bytes into exact-case and optionally case-folded `CD_NAME`.
6. Search or aggregate extents depending on caller.

## Name Handling

Self and parent entries are detected as one-byte directory file IDs `0` and `1` and mapped to fixed Unicode directory names. Non-special entries are converted based on media state:

- Non-Joliet: `RtlOemToUnicodeN`.
- Joliet: `CdConvertBigToLittleEndian`.

After conversion, `CdConvertNameToCdName` splits the semicolon version suffix, trailing periods are removed from the filename portion, and `CdIsLegalName` validates the resulting Unicode filename. Ignore-case searches allocate or split a double-sized buffer so exact and upcased names can coexist.

## Short Name Support

Short-name matching is derived from `CdShortNameDirentOffset` and `CdGenerate8dot3Name`. The generated short name encodes `DirentOffset >> SHORT_NAME_SHIFT` after a tilde, reducing collision risk. `CdFindFile` first tries the disk name, then checks a generated 8.3 alias if the requested name looks like a short-name form and the target dirent offset matches.

## Multi-Extent and CD-XA Behavior

`CdLookupLastFileDirent` walks all dirents for a file until a dirent without `CD_ATTRIBUTE_MULTI` is reached. It sums file sizes across extents. For CD-XA media, it calls `CdCheckForXAExtent` and enforces consistent extent type across all extents. For XA data it validates sector alignment when logical block size is not 2048 and computes visible file size using RIFF header plus `XA_SECTOR_SIZE` per sector.

## Error Handling and Corruption Checks

The file raises `STATUS_FILE_CORRUPT_ERROR` for malformed dirents, zero-length file names, illegal converted names, invalid self/parent ordering with prior allocation, missing multi-extent continuation, inconsistent XA extent types, and invalid XA/interleave alignment. It uses cache-manager BCB unpin cleanup through helper routines rather than direct cleanup in each scan loop.

## Dependencies

Important dependencies include cache mapping (`CcMapData`, `CdUnpinData`), name helpers from `namesup.c`, volume state flags such as `VCB_STATE_JOLIET` and `VCB_STATE_CDXA`, dirent/path structures from CDFS headers, and allocation helpers such as `FsRtlAllocatePoolWithTag` and `CdFreePool`.

## Research Notes

This file is the core bridge between ISO9660/HSG on-disk directory records and CDFS higher-level create, enumeration, and query behavior. Its correctness depends heavily on sector-boundary invariants, BCB lifetime, and preserving dirent-offset identity for short-name synthesis.
