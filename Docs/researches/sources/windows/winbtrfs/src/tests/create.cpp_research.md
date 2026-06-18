# File Research: sources/windows/winbtrfs/src/tests/create.cpp

## Purpose

`create.cpp` is a WinBtrfs native-NT create/open semantics test suite. It validates file and directory creation, create disposition results, case-insensitive name collisions, file information returned after creation, directory enumeration records, share-access rules, path/name validation, UTF-16/UTF-8 edge cases, and `FILE_OPEN_BY_FILE_ID` / object-ID behavior.

It is test code rather than filesystem implementation, but it is valuable because it documents the Windows-observable contract WinBtrfs expects its create path and query-information path to satisfy.

## Main Helpers

- `query_object_basic_information()`
  - Wraps `NtQueryObject(ObjectBasicInformation)`.
  - Verifies returned length exactly matches `OBJECT_BASIC_INFORMATION`.
  - Used to check granted access masks on newly opened handles.
- `has_*` concepts
  - Compile-time checks for fields present in different directory-information structs.
  - Let a single verifier handle many `FILE_*_DIR_INFORMATION` variants.
- `check_dir_entry<T>()`
  - Queries one named directory entry and compares available fields against previously queried `FILE_BASIC_INFORMATION`, `FILE_STANDARD_INFORMATION`, 64-bit file ID, and 128-bit file ID.
  - Checks timestamps, EOF/allocation, attributes, filename length/content, and file ID where that field exists.
- `open_by_id<T>()`
  - Calls `NtCreateFile` with `FILE_OPEN_BY_FILE_ID`.
  - Supports both 64-bit file IDs and 16-byte object IDs.
  - Requires a root directory handle and verifies `IO_STATUS_BLOCK.Information`.
- `create_or_get_object_id()`
  - Issues `FSCTL_CREATE_OR_GET_OBJECT_ID`.
  - Handles pending completion through an event and returns the 16-byte object ID.

## `test_create()` Coverage

The first half of the file exercises ordinary pathname create/open behavior.

- Creates `file` with `FILE_CREATE`, then checks duplicate creation and case-only duplicate creation both fail with `STATUS_OBJECT_NAME_COLLISION`.
- Verifies initial file metadata:
  - `FILE_BASIC_INFORMATION` attributes are `FILE_ATTRIBUTE_ARCHIVE`.
  - `FILE_STANDARD_INFORMATION` has zero allocation/EOF, one link, not delete-pending, not directory.
  - name query ends in `\file`.
  - access, mode, alignment, position, attribute-tag, compression, EA, internal ID, network-open, standard-link, stat, stat-LX, file-ID, and all-information classes are internally consistent.
- Confirms normalized name query requires traverse privilege:
  - without `SeChangeNotifyPrivilege`, normalized-name query returns `STATUS_ACCESS_DENIED`;
  - after enabling that privilege, normalized-name query succeeds and still ends in `\file`.
- Checks directory enumeration output for the same file across:
  - `FILE_DIRECTORY_INFORMATION`
  - `FILE_BOTH_DIR_INFORMATION`
  - `FILE_FULL_DIR_INFORMATION`
  - `FILE_ID_BOTH_DIR_INFORMATION`
  - `FILE_ID_FULL_DIR_INFORMATION`
  - `FILE_ID_EXTD_DIR_INFORMATION`
  - `FILE_ID_EXTD_BOTH_DIR_INFORMATION`
  - `FILE_NAMES_INFORMATION`
- Tests `FILE_NON_DIRECTORY_FILE` and `FILE_DIRECTORY_FILE` interactions:
  - regular file creation with `FILE_NON_DIRECTORY_FILE`;
  - `FILE_ATTRIBUTE_DIRECTORY` is ignored for non-directory creates;
  - directory creation with `FILE_DIRECTORY_FILE`;
  - opening a directory without explicit directory options is accepted;
  - `FILE_ATTRIBUTE_DIRECTORY` alone does not make a regular file a directory.
- Tests attribute normalization:
  - regular files always get archive unless special attributes such as hidden/readonly/system are added;
  - `FILE_ATTRIBUTE_NORMAL` maps to archive for files;
  - directories preserve directory plus hidden/readonly/system, and `FILE_ATTRIBUTE_NORMAL` maps to directory only.
- Tests share access:
  - `FILE_SHARE_READ` allows compatible read opens and rejects write/delete opens;
  - `FILE_SHARE_WRITE` allows compatible write opens and rejects read/delete opens;
  - `FILE_SHARE_DELETE` allows compatible delete opens and rejects read/write opens.
- Tests missing path components and attempting to create/open a child under a regular file, expecting `STATUS_OBJECT_PATH_NOT_FOUND`.
- Tests `FILE_OPEN_IF` creates on first open and reports `FILE_OPENED` on the second open.
- Tests name validation:
  - 256 UTF-16 code units are rejected as too long;
  - emoji names are accepted;
  - more than 255 UTF-8 bytes and unpaired surrogate/WTF-16 sequences are accepted on NTFS but rejected on Btrfs;
  - slash, colon, angle brackets, quote, pipe, question mark, and asterisk are invalid;
  - `CON` is allowed through the NT API.

## `test_open_id()` Coverage

The second half exercises open-by-ID behavior and object IDs.

- Enables `SeChangeNotifyPrivilege` because querying filenames and hard links by ID needs traverse privilege.
- Creates `id1`, writes 4096 random bytes, records its `FILE_INTERNAL_INFORMATION` ID, and verifies directory enumeration exposes the same ID.
- Validates open-by-ID parameter checks:
  - null `RootDirectory` returns `STATUS_INVALID_PARAMETER`;
  - opening a regular file by ID with `FILE_DIRECTORY_FILE` returns `STATUS_NOT_A_DIRECTORY`.
- Opens `id1` by 64-bit file ID, reads data back, checks filename, and verifies one hardlink named `id1`.
- While opened by ID:
  - creating a hardlink is allowed;
  - renaming returns `STATUS_INVALID_PARAMETER`;
  - setting delete disposition returns `STATUS_INVALID_PARAMETER`.
- Opens by ID with `FILE_DELETE_ON_CLOSE`; because the file has two links, both `id1` and `id1a` remain afterward.
- Exercises create dispositions on an existing file ID:
  - `FILE_OPEN_IF` reports opened;
  - `FILE_OVERWRITE_IF` reports overwritten;
  - `FILE_SUPERSEDE` reports superseded;
  - `FILE_CREATE` reports name collision;
  - `FILE_OVERWRITE` reports overwritten.
- Creates and deletes `id2`, then verifies all open-by-ID dispositions against the stale ID fail with `STATUS_INVALID_PARAMETER`.
- Creates directory `id3`, verifies `FILE_NON_DIRECTORY_FILE` fails with `STATUS_FILE_IS_A_DIRECTORY`, and opening without that option succeeds.
- Creates `id4`, POSIX-deletes it through a second handle, then verifies opening the orphaned inode by file ID returns `STATUS_DELETE_PENDING`.
- Creates `id5`, obtains a 16-byte object ID via `FSCTL_CREATE_OR_GET_OBJECT_ID`, and opens it by object ID.
- Disables privileges, opens `id6` by ID, and confirms querying the filename without traverse privilege returns `STATUS_ACCESS_DENIED`.

## Important Dependencies

- Test harness helpers from `test.h` and companion test files:
  - `create_file`, `query_information`, `query_all_information`, `query_file_name_information`
  - `query_dir`, `query_links`, `set_link_information`, `set_rename_information`
  - `set_disposition_information`, `set_disposition_information_ex`
  - `adjust_token_privileges`, `disable_token_privileges`, `write_file`, `read_file`
- Native NT APIs:
  - `NtCreateFile`, `NtQueryObject`, `NtFsControlFile`, `NtWaitForSingleObject`
- Windows file information classes and flags:
  - `FILE_ALL_INFORMATION`, `FILE_STAT_INFORMATION`, `FILE_STAT_LX_INFORMATION`
  - `FILE_ID_INFORMATION`, extended directory information classes
  - `FILE_OPEN_BY_FILE_ID`, create dispositions, share masks, and privilege-sensitive normalized-name query behavior.

## Notable Edge Cases

- The tests intentionally differ expected behavior for NTFS versus Btrfs for names that Linux Btrfs would reject: oversized UTF-8 names and invalid UTF-16 surrogate sequences.
- `check_dir_entry()` has FIXME notes for EA size, short names, and reparse tags, so directory-entry validation is broad but not exhaustive.
- Open-by-ID handles are treated specially: rename/delete through such handles is expected to fail even when other metadata operations such as hardlink creation can succeed.
- `FILE_DELETE_ON_CLOSE` on an ID-opened file with multiple links must not remove all links.
- Filename queries by ID-opened handles remain privilege-sensitive.
