# File Research: sources/windows/reactos/drivers/filesystems/udfs/namesup.cpp

## Role

`namesup.cpp` implements filename parsing, validation, wildcard matching, and 8.3-name eligibility helpers for the UDF driver.

## Core Behavior

- `UDFDissectName()` skips leading backslashes, handles leading stream-colon syntax, and returns the next component boundary while reporting component length. It has an x86/MSVC inline-assembly implementation and a generic C fallback.
- `UDFIsNameValid()` rejects empty and too-long names, rejects Windows-disallowed characters and control characters, detects a single stream separator, forbids nested stream paths, and disallows trailing space or dot before separators and at the end.
- `UDFIsNameInExpression()` first compares a long filename against a search pattern using either `FsRtlIsNameInExpression()` or `RtlCompareUnicodeString()`. If that fails and an 8.3 name is possible, it generates a DOS name through `UDFDOSName()` and retries, setting `DosOpen` when the short-name path matched.
- `UDFIsMatchAllMask()` recognizes match-all patterns: Win32 `*`, DOS all-question-mark `????????.???`, and DOS `*.*`, also identifying DOS-open semantics.
- `UDFCanNameBeA8dot3()` checks whether a name fits a single-dot, 8-character basename, 3-character extension shape.

## Dependencies

The code depends on Windows Unicode strings, FsRtl wildcard matching, RTL string comparison, UDF DOS-name generation, UDF path-length constants, and DOS wildcard character constants.

## Notable Risks

- `UDFIsNameValid()` uses `c0` to validate separators and trailing characters after the first character; malformed first-character edge cases are worth testing carefully when changing validation.
- The x86 inline-assembly and generic C versions of `UDFDissectName()` must remain behaviorally identical.
- Alternate stream syntax is accepted through `:`, but sub-streams and stream directories are deliberately rejected.
