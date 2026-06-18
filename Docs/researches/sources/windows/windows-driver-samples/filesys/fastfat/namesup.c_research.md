# File Research: sources/windows/windows-driver-samples/filesys/fastfat/namesup.c

## Purpose
Provides FAT name conversion and selection support: wildcard matching, 8.3 conversion, long-name reconstruction, OEM/Unicode conversion, generated short-name selection, and case-bit handling.

## Main Entry Points
- `FatIsNameInExpression`: wildcard expression match for upcased OEM names.
- `FatStringTo8dot3`: converts an OEM string into the 11-byte FAT 8.3 directory-entry format.
- `Fat8dot3ToString`: converts a FAT 8.3 dirent name back into an OEM string, optionally restoring case.
- `FatGetUnicodeNameFromFcb`: obtains the Unicode long name for an FCB, or manufactures one from the short name.
- `FatSetFullFileNameInFcb`: lazily builds and stores the full Unicode path in an FCB.
- `FatUnicodeToUpcaseOem`: converts Unicode to upcased OEM with fallback allocation.
- `FatSelectNames`: chooses whether to use an input OEM name directly, generate an 8.3 short name, and/or create an LFN.
- `FatEvaluateNameCase`: decides whether FAT case flags are enough or an LFN is required.
- `FatSpaceInName`: detects spaces in a Unicode name.
- `FatUnicodeRestoreShortNameCase`: downcases 8.3 name and extension segments based on FAT NT case flags.

## Behavior
`FatStringTo8dot3` starts with an 11-byte space-filled output, copies the base name until a dot or length limit, then copies the extension into bytes 8 through 10. It translates a first byte of `0xe5` to FAT’s special `0x05` stored representation.

`Fat8dot3ToString` trims trailing spaces from base and extension fields, inserts a dot if an extension exists, restores the special first-character `0x05` back to `0xe5`, and optionally downcases base or extension letters using `Dirent->NtByte` flags. It carefully skips DBCS lead-byte sequences when applying ASCII case restoration.

`FatGetUnicodeNameFromFcb` locates the directory entry for an FCB, validates the located offset, and returns an LFN if present. If no LFN exists, it converts the restored short OEM name to Unicode. If the expected LFN/dirent relationship is inconsistent, it raises `STATUS_FILE_INVALID`.

`FatSetFullFileNameInFcb` lazily constructs a full path by walking parent DCBs toward the root. It reuses an ancestor’s cached full name when available, allocates a full-name buffer, then fills path components backward using `FatGetUnicodeNameFromFcb`.

`FatUnicodeToUpcaseOem` first tries conversion into caller-provided storage. If the buffer is too small, it lets the runtime allocate. Unmappable characters are represented by setting destination length to zero; other failures are normalized and raised.

`FatSelectNames` determines whether the proposed OEM name can be stored directly as a FAT short name. It forces short-name generation if the OEM name is empty, invalid as short OEM, or if the Unicode name contains a space. It optionally tries a caller-supplied short-name candidate before using `RtlGenerate8dot3Name`, checking each candidate against the parent directory with `FatLocateSimpleOemDirent`.

`FatEvaluateNameCase` implements the Chicago-mode case optimization decision: if the Unicode name is otherwise 8.3-compatible and case can be represented by the base/extension lowercase bits, no LFN is needed. Mixed case within a component or code-page invariant non-ASCII cases force LFN creation.

## Dependencies
- `FsRtlIsDbcsInExpression`
- `FsRtlIsLeadDbcsCharacter`
- `RtlGenerate8dot3Name`
- `RtlUnicodeStringToCountedOemString`
- `RtlUpcaseUnicodeStringToCountedOemString`
- `RtlOemStringToCountedUnicodeString`
- `RtlDowncaseUnicodeString`
- `FatLocateDirent`
- `FatLocateSimpleOemDirent`
- `FatIsNameShortOemValid`
- `FatUnpinBcb`

## Important Notes
This file encodes several FAT compatibility details: the deleted-entry `0xe5` escape, DBCS-safe case restoration, Chicago-mode case flags, generated short-name collision checks, and full-path lazy caching. It is a core dependency for create, lookup, directory enumeration, and rename behavior.
