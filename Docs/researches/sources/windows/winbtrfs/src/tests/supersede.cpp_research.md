# File Research: sources/windows/winbtrfs/src/tests/supersede.cpp

## Purpose

`supersede.cpp` is a focused test for `FILE_SUPERSEDE` create disposition behavior.

## Main Entrypoint

- `test_supersede(const u16string& dir)`

## Behavior Covered

The test first creates a file using `FILE_SUPERSEDE` with `FILE_ATTRIBUTE_READONLY` and verifies that the resulting attributes include both `FILE_ATTRIBUTE_READONLY` and `FILE_ATTRIBUTE_ARCHIVE`.

It then supersedes an already open file while share modes allow read/write/delete sharing, expecting `FILE_SUPERSEDED`. After closing, it supersedes again with no special attributes and verifies that the archive bit remains.

Attribute clearing is tested for hidden and system files. Superseding while clearing `FILE_ATTRIBUTE_HIDDEN` or `FILE_ATTRIBUTE_SYSTEM` is expected to fail with `STATUS_ACCESS_DENIED`.

Directory supersede behavior is intentionally rejected: creating a directory with `FILE_SUPERSEDE | FILE_DIRECTORY_FILE` should return `STATUS_INVALID_PARAMETER`.

The final case validates case behavior. A file created as `supersede2` is superseded through path `SUPERSEDE2`, but `FileNameInformation` is expected to still end with `\supersede2`, documenting case-preserving behavior for supersede on an existing file.

## Integration Points

Uses shared harness helpers `create_file`, `query_information`, `query_file_name_information`, `exp_status`, and `formatted_error`.

## Research Notes

This small file isolates disposition semantics that overlap with overwrite and rename tests but are cleaner here: attribute inheritance/reset, hidden/system protection, directory invalidity, and case preservation.
