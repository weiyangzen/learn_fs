# File Research: sources/windows/winbtrfs/src/tests/rename.cpp

## Purpose

`rename.cpp` is the WinBtrfs test-suite coverage for Windows rename semantics. It exercises both legacy `FileRenameInformation` and Windows 10 1709+ `FileRenameInformationEx`, with particular focus on NT status compatibility, security checks, case behavior, target replacement, POSIX rename semantics, directory handling, and special name validation.

## Main Entrypoints

- `set_rename_information(...)`: builds `FILE_RENAME_INFORMATION`, calls `NtSetInformationFile(..., FileRenameInformation)`, and asserts `iosb.Information == 0`.
- `set_rename_information_ex(...)`: builds `FILE_RENAME_INFORMATION_EX`, calls `NtSetInformationFile(..., FileRenameInformationEx)`, and asserts `iosb.Information == 0`.
- `test_rename(const u16string& dir)`: legacy rename behavior tests.
- `test_rename_ex(HANDLE token, const u16string& dir)`: extended rename flag behavior tests.

## Behavior Covered

`test_rename` validates basic file and directory renames, same-name renames, case-only renames, overwriting existing files with and without `ReplaceIfExists`, and expected failures when the target is open. It verifies post-rename state through both `FileNameInformation` and directory enumeration.

The file covers moves across directories, including absolute target paths and relative target names under a `RootDirectory` handle. It also verifies sharing side effects when a directory handle prevents enumeration, and confirms old entries disappear while new entries appear.

Permission-sensitive coverage is extensive. Tests assert that renaming requires source `DELETE`, that the destination parent needs `FILE_ADD_FILE` or `FILE_ADD_SUBDIRECTORY`, and that replacing a target requires either target `DELETE` or parent `FILE_DELETE_CHILD`. It includes denied cases for missing parent access, missing source delete access, and overwriting targets protected by DACLs.

Type and attribute handling are explicitly tested. File-over-directory and directory-over-file replacement are expected to fail. Readonly targets reject replacement unless extended flags override that later. System targets can be replaced. Empty directory replacement has different behavior under extended POSIX semantics.

Name validation covers Windows-invalid characters, too-long UTF-8 names, and malformed UTF-16 surrogate sequences. The expected status depends on `fstype`: NTFS may accept names that WinBtrfs rejects as `STATUS_OBJECT_NAME_INVALID`.

`test_rename_ex` adds coverage for:
- `FILE_RENAME_REPLACE_IF_EXISTS`
- `FILE_RENAME_IGNORE_READONLY_ATTRIBUTE`
- `FILE_RENAME_POSIX_SEMANTICS`
- sharing violations when POSIX replacement target lacks `FILE_SHARE_DELETE`
- orphaned replaced files remaining usable through open handles
- `FILE_STANDARD_INFORMATION`, `FILE_STANDARD_LINK_INFORMATION`, and hardlink enumeration after POSIX replacement
- directory replacement with POSIX semantics, including non-empty directory failure
- mapped `SEC_IMAGE` targets rejecting normal and POSIX replacement

## Integration Points

This file depends heavily on shared helpers from `test.cpp` and `test.h`: `create_file`, `query_dir`, `query_file_name_information`, `query_information`, `query_links`, `set_disposition_information`, `set_dacl`, `create_section`, `pe_image`, `adjust_token_privileges`, and `disable_token_privileges`.

## Research Notes

This is one of the strongest compatibility oracles in the test suite because it encodes exact NTSTATUS expectations for subtle rename cases. The POSIX semantics section is especially important for implementing Windows behavior over Btrfs inode/link semantics, since it checks delete-pending state, accessible link counts, total link counts, and renamed/orphaned link visibility.

## Open FIXMEs In File

The file notes missing coverage for security descriptor changes after cross-directory moves, inability to rename the root directory, and several newer `FILE_RENAME_*` storage reserve/pin-state flags.
