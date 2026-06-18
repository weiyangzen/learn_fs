# File Research: sources/windows/reactos/drivers/filesystems/fastfat/namesup.c

This file implements FastFAT name conversion, matching, case restoration, long-name lookup, full-path construction, and short-name selection.

Key responsibilities:
- Match upcased OEM names against wildcard expressions with `FsRtlIsDbcsInExpression`.
- Convert between user-visible OEM names and FAT on-disk 8.3 directory-entry format.
- Restore lowercase display case from FAT `NtByte` case bits in Chicago compatibility mode.
- Locate and synthesize Unicode names for existing FCBs, using LFN entries when present and short-name conversion otherwise.
- Lazily build `Fcb->FullFileName` by walking parent DCBs and reusing ancestor full names when available.
- Convert Unicode names to upcased OEM names, allocating dynamically on buffer overflow and treating unmappable characters as zero-length OEM names.
- Decide whether create paths can use a supplied 8.3 name directly or must generate a collision-free short name with `RtlGenerate8dot3Name`.
- Decide whether a long filename entry is required based on mixed case, spaces, extended characters, and code-page invariance.
- Restore Unicode 8.3 case segments from separate base-name and extension lowercase flags.

Important functions:
- `FatIsNameInExpression`: wildcard matching for already-upcased OEM names.
- `FatStringTo8dot3`: packs a legal short OEM string into the 11-byte FAT dirent name field, including the special leading `0xe5` to `0x05` translation.
- `Fat8dot3ToString`: expands a FAT 8.3 dirent name into an OEM string, trims padding, adds the dot when needed, restores `0xe5`, and optionally lowercases base/extension from case bits.
- `FatGetUnicodeNameFromFcb`: rereads the directory entry for an FCB and returns the exact Unicode LFN or a Unicode-converted short name.
- `FatSetFullFileNameInFcb`: constructs a full path from parent components and caches it in the FCB.
- `FatUnicodeToUpcaseOem`: wrapper around `RtlUpcaseUnicodeStringToCountedOemString` with retry allocation and FAT-specific error handling.
- `FatSelectNames`: chooses the short name and whether an LFN must be created, trying a suggested short name before generated names.
- `FatEvaluateNameCase`: calculates lowercase case-bit eligibility and whether an LFN is required.
- `FatSpaceInName`: detects spaces that force short-name generation.
- `FatUnicodeRestoreShortNameCase`: downcases base and/or extension portions of a Unicode short name.

Notable behavior and risks:
- Name handling depends on global compatibility flags `FatData.ChicagoMode` and `FatData.CodePageInvariant`.
- LFN reconstruction validates that the located dirent offset matches the FCB’s expected dirent; mismatches raise `STATUS_FILE_INVALID`.
- `FatSetFullFileNameInFcb` allocates a temporary max-LFN buffer and frees partially built full names on abnormal unwind.
- Short-name generation loops until `FatLocateSimpleOemDirent` proves a candidate does not exist in the parent directory.
