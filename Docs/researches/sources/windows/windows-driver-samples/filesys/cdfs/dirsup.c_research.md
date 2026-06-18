# File Research: sources/windows/windows-driver-samples/filesys/cdfs/dirsup.c

## Purpose

Provides low-level CDFS directory-entry support: mapping directory sectors, walking raw dirents, validating bounds, converting raw dirents into in-memory `DIRENT` structures, building Unicode names, searching for files/directories, grouping multi-extent entries, computing file sizes, detecting XA extents, and cleaning enumeration contexts.

## Main Entry Points

- `CdLookupDirent`
- `CdLookupNextDirent`
- `CdUpdateDirentFromRawDirent`
- `CdUpdateDirentName`
- `CdFindFile`
- `CdFindDirectory`
- `CdFindFileByShortName`
- `CdLookupNextInitialFileDirent`
- `CdLookupLastFileDirent`
- `CdCleanupFileContext`
- `CdCheckRawDirentBounds`
- `CdCheckForXAExtent`

## Directory Walking

Directories are treated as contiguous sectors. `CdLookupDirent` maps the sector containing a known dirent offset, truncating length at EOF, and validates the raw dirent with `CdCheckRawDirentBounds`.

`CdLookupNextDirent` finds the next possible dirent. It can reuse or remap a sector, advances by `NextDirentOffset`, skips all-zero sector tails, maps the next sector when needed, and validates each nonzero candidate. It supports `CurrentDirContext` and `NextDirContext` pointing to the same structure.

`CdCheckRawDirentBounds` rejects corrupt records when the raw dirent length exceeds remaining mapped bytes, is smaller than the minimum raw dirent size, or cannot contain the declared file-id length. A return of zero means the next search should move to the next sector.

## Raw Dirent Conversion

`CdUpdateDirentFromRawDirent` copies unaligned on-disk fields safely into `DIRENT`:

- `DirentOffset`
- raw dirent length
- starting logical block plus XAR length
- data length
- timestamp pointer
- dirent flags
- interleave fields
- file-name pointer and length
- possible system-use offset
- XA defaults

It rejects zero-length file names with `STATUS_FILE_CORRUPT_ERROR`.

`CdUpdateDirentName` turns raw ISO/HSG/Joliet bytes into CDFS Unicode name/version fields. It handles constant directory entries where a one-byte name of 0 or 1 maps to `.` or `..`. It allocates a larger buffer when embedded storage is insufficient, converts OEM names to Unicode for non-Joliet discs, converts big-endian Unicode for Joliet discs, splits name and version with `CdConvertNameToCdName`, strips a trailing period before a version string, validates legal names, and optionally builds an uppercase comparison name.

## Search Functions

`CdFindFile` searches only non-directory, non-associated entries. It compares long CDFS names first, then tries a generated 8.3 short name when the requested name can refer to a short-name offset and the candidate long name is not already 8.3. On success it calls `CdLookupLastFileDirent`.

`CdFindDirectory` searches directory entries only and does not use short-name equivalence.

`CdFindFileByShortName` uses the encoded short-name dirent offset. Since raw dirents are at least 34 bytes, one shifted 32-byte bucket can identify at most one dirent. It walks until the matching bucket, rejects associated and already-8.3 entries, generates the 8.3 name, compares, and collects all dirents on success.

## Multi-Extent and XA Handling

`CdLookupNextInitialFileDirent` advances to the first dirent of the next file, skipping any remaining multi-extent dirents for the current file. It rotates `PriorDirent`, `InitialDirent`, and `CurrentDirent` slots in `FILE_ENUM_CONTEXT`, clears file size and flags, and leaves the context positioned at the next file's initial dirent.

`CdLookupLastFileDirent` starts from a matching initial dirent and walks all `CD_ATTRIBUTE_MULTI` extents. It computes total file size. For CD-XA media, it calls `CdCheckForXAExtent`, verifies consistent extent type across all extents, enforces sector alignment when logical block size is not 2048 bytes, accounts for RIFF header size on first XA extent, and uses XA sector payload sizing for Mode2 Form2 data. Corrupt multi-extent chains raise `STATUS_FILE_CORRUPT_ERROR`.

`CdCheckForXAExtent` scans the system-use area for the XA signature and records audio, Mode2 Form2, XA attributes, and XA file number.

## Cleanup

`CdCleanupFileContext` unpins all mapped dirent contexts and frees allocated name buffers for all compound dirent slots in the file enumeration context.

## Dependencies

Key dependencies include cache manager mapping (`CcMapData`), CDFS unpin/cleanup helpers, raw ISO/HSG macros, name conversion helpers, short-name generation helpers, and VCB state flags such as `VCB_STATE_JOLIET` and `VCB_STATE_CDXA`.
