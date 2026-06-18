# File Research: sources/windows/winfsp/src/sys/name.c

## Purpose

`name.c` validates and manipulates WinFsp file names, stream names, wildcard patterns, EA names, and name-expression matches.

## Main Contents

- `FspFileNameIsValid`
- `FspFileNameIsValidPattern`
- `FspEaNameIsValid`
- `FspFileNameSuffix`
- `FspFileNameInExpression`

## File Name Validation

`FspFileNameIsValid` checks:

- Nonempty even-byte UTF-16 length.
- Component length does not exceed `MaxComponentLength`.
- No doubled backslashes inside the path.
- Stream names only appear in the final path component.
- Colon use is rejected unless stream parsing outputs were requested.
- ASCII characters are checked with `FsRtlTestAnsiCharacter`.
- Stream type, if present, must be `$DATA` case-insensitively.
- A stream name without a stream type must be nonempty.

If a stream is accepted, `StreamPart` points into the original path buffer and `StreamType` is set to none or data.

## Pattern Validation

`FspFileNameIsValidPattern` permits wildcard characters but rejects:

- Backslashes.
- Colons.
- Invalid ASCII characters under NTFS legal-name rules.
- Components longer than the maximum.

## EA Name Validation

`FspEaNameIsValid` follows FastFAT-like rules:

- Length must be 1 through 254 bytes.
- DBCS lead bytes are skipped as a pair.
- Other bytes must be legal FAT ANSI characters.

## Path Splitting

`FspFileNameSuffix` splits a path into:

- `Remain`: everything before the final component.
- `Suffix`: the final component after the last run of backslashes.

It preserves root-style remain length for a path beginning with `\`.

## Expression Matching

`FspFileNameInExpression` wraps `FsRtlIsNameInExpression` in exception handling and asserts that custom upcase tables are not supported.

## Notable Details

- The stream parsing routine mutates only output `UNICODE_STRING` descriptors; it does not copy path text.
- Non-ASCII file-name characters bypass the ASCII `FsRtlTestAnsiCharacter` check.
- `FspFileNameSuffix` tolerates multiple backslashes while suffix extraction does; strict validity checking separately rejects doubled backslashes.
