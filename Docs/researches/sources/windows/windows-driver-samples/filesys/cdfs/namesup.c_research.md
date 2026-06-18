# File Research: sources/windows/windows-driver-samples/filesys/cdfs/namesup.c

## Purpose

Provides CDFS name manipulation support: ISO/Joliet byte conversion, name/version splitting, upcasing, path component dissection, legal-name checks, 8.3 short-name generation, wildcard matching, embedded short-name offset decoding, and lexical name comparison.

## Main Entry Points

- `CdConvertNameToCdName`
- `CdConvertBigToLittleEndian`
- `CdUpcaseName`
- `CdDissectName`
- `CdIsLegalName`
- `CdIs8dot3Name`
- `CdGenerate8dot3Name`
- `CdIsNameInExpression`
- `CdShortNameDirentOffset`
- `CdFullCompareNames`

## Key Behavior

`CdConvertNameToCdName` splits a Unicode file name at `;`, making the suffix after the separator the version string when present.

`CdConvertBigToLittleEndian` converts Joliet big-endian Unicode bytes into little-endian form and raises `STATUS_DISK_CORRUPT_ERROR` on odd byte counts.

`CdUpcaseName` upcases both filename and version portions using `RtlUpcaseUnicodeString`. When producing a separate destination, it lays the version string after the filename and inserts the `;` separator.

`CdDissectName` removes one backslash-delimited path component from a remaining name and returns that component as `FinalName`.

`CdIsLegalName` validates characters against HPFS legality, while allowing `"`, `<`, `>`, and `|` for CDFS compatibility.

`CdIs8dot3Name` enforces short-name shape: limited length, no spaces, at most one dot, base length constraints, and OEM/FAT legality via `FsRtlIsFatDbcsLegal`.

`CdGenerate8dot3Name` calls `RtlGenerate8dot3Name`, then biases the result with a `~` plus a hexadecimal dirent-offset-derived value. It accounts for DBCS byte width when deciding how much base name can precede the suffix.

`CdIsNameInExpression` compares CDFS names against search expressions. It supports wildcard matching independently for file name and version string, and can skip version checking when requested.

`CdShortNameDirentOffset` parses a `~HEX` sequence before the dot and returns the decoded offset bucket, or `MAXULONG` if no valid sequence exists.

`CdFullCompareNames` performs a case-sensitive binary lexical comparison used by prefix splay trees.

## Dependencies

Uses `RtlGenerate8dot3Name`, Unicode/OEM conversion routines, FsRtl name-expression matching, FAT/HPFS legality helpers, and CDFS `CD_NAME` conventions shared with directory and prefix lookup code.
