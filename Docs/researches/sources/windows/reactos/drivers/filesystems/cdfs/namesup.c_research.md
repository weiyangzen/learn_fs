# File Research: sources/windows/reactos/drivers/filesystems/cdfs/namesup.c

## Purpose

`namesup.c` implements CDFS name manipulation: splitting ISO version suffixes, endian conversion for Joliet names, uppercasing, path component dissection, legal-name checks, 8.3 validation/generation, wildcard matching, short-name offset extraction, and direct lexical comparison.

## Main Functions

- `CdConvertNameToCdName`: splits a `CD_NAME` file name at `;`. The filename portion remains in `FileName`; bytes after the semicolon become `VersionString` when present.
- `CdConvertBigToLittleEndian`: converts a big-endian Unicode byte stream into little-endian form. Odd byte counts raise `STATUS_DISK_CORRUPT_ERROR`.
- `CdUpcaseName`: upcases both filename and version string portions, inserting a semicolon separator into the destination buffer when copying into a separate `CD_NAME`.
- `CdDissectName`: removes the first path component from `RemainingName` and returns it in `FinalName`, advancing past a backslash if more components remain.
- `CdIsLegalName`: checks Unicode characters against HPFS legality while explicitly allowing `"`, `<`, `>`, and `|` for CDFS behavior.
- `CdIs8dot3Name`: validates whether a Unicode name is legal 8.3/FAT-style form, rejecting spaces, excess length, excess dots, dots past the base-name limit, and names that cannot convert to legal OEM DBCS FAT names.
- `CdGenerate8dot3Name`: creates a synthetic short name from a long Unicode name and dirent offset.
- `CdIsNameInExpression`: matches a current `CD_NAME` against a search expression, using `FsRtlIsNameInExpression` when wildcard flags are set and exact memory comparison otherwise. It can optionally match version strings.
- `CdShortNameDirentOffset`: parses a tilde plus hexadecimal offset string from a name before any dot; returns `MAXULONG` if not found or invalid.
- `CdFullCompareNames`: performs fast case-sensitive lexical comparison via `RtlCompareMemory`, resolving equal prefixes by shorter length.

## 8.3 Generation Details

`CdGenerate8dot3Name` first calls `RtlGenerate8dot3Name` to obtain a generic Unicode short name. It then biases the base name by inserting `~` plus the hexadecimal representation of `DirentOffset >> SHORT_NAME_SHIFT`. It carefully accounts for DBCS lead bytes in the OEM representation so the generated name remains within the 8-character base limit. The extension portion, if present, is copied after the biased base.

## Wildcard and Version Matching

`CdIsNameInExpression` independently checks file name and version string portions. Version matching occurs only when requested, when the search expression contains a version, and when the wildcard flags do not indicate version-match-all. Wildcards are delegated to `FsRtlIsNameInExpression`; non-wildcard paths use direct length and byte comparison.

## Endian and Joliet Support

Joliet directory and volume strings are big-endian Unicode on disk. `CdConvertBigToLittleEndian` is the shared primitive used by both name conversion and volume-label handling. It treats odd byte counts as corrupt media.

## Dependencies

This file depends on Windows RTL string conversion and name routines, `FsRtl` wildcard/FAT-name helpers, CDFS name structures, wildcard flags in CCB state, and short-name constants such as `BYTE_COUNT_8_DOT_3` and `SHORT_NAME_SHIFT`.

## Research Notes

This file defines the name semantics used by create, directory enumeration, alternate-name queries, and volume verification. The generated short-name scheme is deterministic and tied to dirent offset, not stored on disk.
