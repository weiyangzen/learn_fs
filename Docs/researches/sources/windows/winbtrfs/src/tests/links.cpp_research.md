# File Research: sources/windows/winbtrfs/src/tests/links.cpp

## Purpose

`links.cpp` is the WinBtrfs user-mode integration test coverage for Windows hardlink semantics. It exercises `FileHardLinkInformation`, `FileLinkInformation`, and `FileLinkInformationEx` against real file handles and directory entries, validating the driver's link counts, accessible link counts, delete-pending behavior, replacement rules, security checks, POSIX replacement behavior, and mapped-image protections.

The file is not filesystem implementation code, but it is an executable specification for how WinBtrfs should match NTFS/Windows namespace behavior when Btrfs inodes have multiple directory entries.

## Helper Functions

- `query_links` calls `NtQueryInformationFile(..., FileHardLinkInformation)` twice: first to discover `FILE_LINKS_INFORMATION.BytesNeeded`, then to retrieve and parse all `FILE_LINK_ENTRY_INFORMATION` records into `(ParentFileId, FileName)` pairs.
- `set_link_information` builds a variable-length `FILE_LINK_INFORMATION` buffer and calls `NtSetInformationFile(..., FileLinkInformation)`.
- `set_link_information_ex` does the same for `FILE_LINK_INFORMATION_EX` and `FileLinkInformationEx`, passing Windows link flags such as `FILE_LINK_REPLACE_IF_EXISTS`, `FILE_LINK_IGNORE_READONLY_ATTRIBUTE`, and `FILE_LINK_POSIX_SEMANTICS`.

All helpers enforce exact success status and expected `IO_STATUS_BLOCK.Information` values, so unexpected partial success or unusual NTSTATUS results fail the test immediately.

## `test_links` Coverage

`test_links` starts by enabling `SeChangeNotifyPrivilege`, because hardlink enumeration requires traverse privilege in this test environment. It then covers classic `FileLinkInformation` behavior.

Basic hardlink creation and enumeration:

- Creates `link1a`, verifies `FileNameInformation`, `FILE_STANDARD_INFORMATION.NumberOfLinks`, and `FILE_STANDARD_LINK_INFORMATION`.
- Creates `link1b` as a hardlink to the same inode.
- Verifies both link names are returned by `FileHardLinkInformation` with the same parent file ID.
- Opens both names and verifies their `FILE_INTERNAL_INFORMATION.IndexNumber` values match.
- Checks `FILE_ID_FULL_DIR_INFORMATION` directory entries for both links and verifies both expose the same file ID.

Delete-pending and link-count accounting:

- Marks one open link delete-pending with `set_disposition_information`.
- Verifies that the delete-pending handle reports one accessible link but two total links.
- Verifies the other link is still accessible and not delete-pending.
- After closing handles, verifies the deleted directory entry is gone while the surviving link remains.
- Tests `FILE_DELETE_ON_CLOSE` combined with hardlink creation, confirming that the newly created link survives close and link counts stay correct.

Rejected hardlink cases:

- Creating a hardlink to a directory returns `STATUS_FILE_IS_A_DIRECTORY`.
- Replacing an existing file without `ReplaceIfExists` returns `STATUS_OBJECT_NAME_COLLISION`.
- Replacing an existing directory returns `STATUS_ACCESS_DENIED`.
- Replacing an open target file without compatible semantics returns `STATUS_ACCESS_DENIED`.
- Creating a link inside a non-directory path returns `STATUS_INVALID_PARAMETER`.
- Linking into a nonexistent directory returns `STATUS_OBJECT_PATH_NOT_FOUND`.

Root-directory handle and sharing behavior:

- Creating a link relative to a directory handle without `FILE_SHARE_WRITE` fails with `STATUS_SHARING_VIOLATION`.
- Creating through a directory handle opened with `FILE_SHARE_WRITE` succeeds.
- The resulting links are verified to live in different parent directories by comparing hardlink parent file IDs.

Replacement and same-name behavior:

- Replacing a normal existing file succeeds when `ReplaceIfExists` is true.
- Re-linking to the same name with replacement is treated as a no-op and leaves `NumberOfLinks == 1`.
- Re-linking the same file with different case updates the visible name casing while keeping one link.
- Overwriting a readonly target with classic `FileLinkInformation` fails with `STATUS_ACCESS_DENIED`.

Name validation:

- Rejects invalid Windows filename characters: `/`, `:`, `<`, `>`, `"`, `|`, `?`, and `*`.
- Checks names whose UTF-8 expansion exceeds 255 bytes.
- Checks malformed UTF-16 surrogate sequences.
- The long UTF-8 and WTF-16 expectations are conditional: NTFS accepts them, while WinBtrfs is expected to return `STATUS_OBJECT_NAME_INVALID`.

ACL and access checks:

- Creating a hardlink in a directory with `SYNCHRONIZE | FILE_ADD_FILE` succeeds.
- Creating in a directory with no relevant permission fails.
- Replacing an existing file requires either directory delete-child permission or delete permission on the target, depending on the case.
- The test verifies combinations where directory ACLs and target file ACLs separately permit or deny replacement.

## `test_links_ex` Coverage

`test_links_ex` covers `FileLinkInformationEx`, including newer Windows link flags.

Extended replacement flags:

- Without `FILE_LINK_REPLACE_IF_EXISTS`, replacing an existing target fails with `STATUS_OBJECT_NAME_COLLISION`.
- With `FILE_LINK_REPLACE_IF_EXISTS`, replacement succeeds.
- Replacing a readonly target fails unless `FILE_LINK_IGNORE_READONLY_ATTRIBUTE` is also present.

POSIX replacement behavior:

- Uses `FILE_LINK_REPLACE_IF_EXISTS | FILE_LINK_POSIX_SEMANTICS` to replace an open target that was opened with `FILE_SHARE_DELETE`.
- Verifies the source file now has two visible links.
- Verifies the replaced target handle becomes delete-pending with zero accessible links but one total link.
- Confirms the old target no longer owns the visible target name and cannot clear its delete bit (`STATUS_FILE_DELETED`).
- Confirms the orphaned target handle remains readable/writable and has a hardlink entry in a different hidden parent directory, matching the Windows model where the old inode is moved away from the visible namespace.
- Verifies POSIX replacement fails with `STATUS_SHARING_VIOLATION` when the open target lacks `FILE_SHARE_DELETE`.

Mapped image-section protections:

- Builds a small PE image using `pe_image`, creates a `SEC_IMAGE` section, and verifies replacement by hardlink fails with `STATUS_ACCESS_DENIED`.
- Repeats the mapped-image replacement test with `FILE_LINK_POSIX_SEMANTICS`; this also must fail.

The file leaves `FIXME` notes for additional `FileLinkInformationEx` storage reserve flags and broader POSIX semantics coverage.

## Dependencies and Cross-File Interactions

This test depends on shared test harness helpers from `test.h`, including:

- Handle wrappers and file creation helpers: `unique_handle`, `create_file`.
- Query helpers: `query_information`, `query_file_name_information`, `query_dir`.
- Mutation helpers: `set_disposition_information`, `set_rename_information`, `set_dacl`.
- I/O helpers: `write_file`, `read_file`.
- Assertion helpers: `test`, `exp_status`, `formatted_error`, `ntstatus_error`.
- Token and privilege helpers: `adjust_token_privileges`, `disable_token_privileges`.
- Image-section helpers from `mmap.cpp`: `pe_image` and `create_section`.

It directly validates behavior implemented in WinBtrfs namespace and metadata paths, especially the hardlink and replacement portions of `fileinfo.c`.

## Edge Cases and Risks

- The test encodes NTFS comparison behavior in a few places, especially around invalid UTF-16 and long UTF-8 names. This matters because WinBtrfs intentionally differs from NTFS where Btrfs name encoding rules are stricter.
- Hardlink enumeration order is not assumed; tests accept either ordering for two-link cases.
- POSIX replacement has subtle dual-object behavior: the new visible target and the old still-open target must report different link states while both handles remain valid.
- The mapped-image tests are important because replacement/delete behavior must coordinate with Windows section objects and image-section truncation rules.

## Research Summary

`links.cpp` is a dense behavioral regression suite for Windows hardlinks on WinBtrfs. It validates normal link creation, link enumeration, visible name casing, directory-relative link creation, delete-pending accounting, ACL enforcement, replacement rules, POSIX unlink-style replacement, readonly override semantics, and image-section safety. It should be read alongside WinBtrfs `fileinfo.c`, because most of the tested behavior maps directly to `set_link_information`, rename/replacement logic, hardlink enumeration, delete disposition, and file information query paths.
