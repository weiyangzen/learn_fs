# File Research: sources/windows/winbtrfs/src/tests/reparse.cpp

## Purpose

`reparse.cpp` tests WinBtrfs handling of reparse points: symbolic links, mount points, Microsoft-owned generic tags, third-party GUID tags, directory reparse points, alternate-stream reparse points, privilege requirements, tag/GUID conflict rules, and query/open behavior with and without `FILE_OPEN_REPARSE_POINT`.

## Main Helpers

- `set_symlink(...)`: constructs `REPARSE_DATA_BUFFER` with `IO_REPARSE_TAG_SYMLINK`.
- `set_mount_point(...)`: constructs mount point reparse data with null-terminated substitute and print names.
- `set_ms_reparse_point(...)`: sets Microsoft-style generic reparse data without GUID.
- `set_reparse_point_guid(...)`: sets non-Microsoft generic reparse data with `REPARSE_GUID_DATA_BUFFER`.
- `query_reparse_point(...)` and `query_reparse_point_guid(...)`: issue `FSCTL_GET_REPARSE_POINT`.
- `delete_reparse_point(...)` and `delete_reparse_point_guid(...)`: issue `FSCTL_DELETE_REPARSE_POINT`.
- `check_reparse_dirent<T>(...)`: validates directory enumeration name and tag reporting across multiple directory information classes.

## Behavior Covered

The test begins by enabling `SeCreateSymbolicLinkPrivilege`, then creates target/source files and verifies relative symlink behavior. It checks that opening without `FILE_OPEN_REPARSE_POINT` resolves to the target ID, while opening with it returns the link object ID.

It verifies that symlink and mount-point attributes surface through:
- `FILE_BASIC_INFORMATION`
- `FILE_EA_INFORMATION`
- `FILE_STAT_INFORMATION`
- `FILE_STAT_LX_INFORMATION`
- `FILE_ATTRIBUTE_TAG_INFORMATION`
- multiple `NtQueryDirectoryFile` directory information classes

Deletion behavior is tested for wrong tags, correct tags, repeated delete attempts, and querying after deletion. Tag mismatch and `STATUS_NOT_A_REPARSE_POINT` are explicitly asserted.

The symlink section covers overwrite semantics: overwriting through a symlink affects the target, while opening with `FILE_OPEN_REPARSE_POINT` overwrites the link object. It also covers invalid reparse data on non-empty files, symlinks with EAs, invalid targets, absolute symlinks, and directory symlinks.

Mount point coverage includes setting on directories, opening through mount points, preserving directory attributes, resolving child paths, rejecting mount points on files, rejecting mount points on non-empty directories unless tag semantics permit it, and tag mismatch when changing an existing mount point to symlink.

Generic reparse tags are split into Microsoft-owned and GUID-backed non-Microsoft forms. The tests verify set/query/update/delete behavior, required GUID use for non-Microsoft tags, conflict statuses for wrong GUIDs, tag mismatch for changed tags, and open failures without `FILE_OPEN_REPARSE_POINT` when the tag is not handled.

Directory reparse points are tested for both Microsoft and GUID tags. A special fake Microsoft directory tag with the directory bit set is allowed on a non-empty directory and can be opened without `FILE_OPEN_REPARSE_POINT`, documenting the “D bit” behavior.

The end of the file validates access requirements. Setting symlinks without sufficient handle access fails, both `FILE_WRITE_ATTRIBUTES` and `FILE_WRITE_DATA` paths are accepted in specific cases, symlink creation fails without `SeCreateSymbolicLinkPrivilege`, while mount points and generic reparse tags do not require that symlink privilege.

Alternate data streams receive dedicated reparse coverage: streams can receive symlink, Microsoft generic, and GUID generic tags; mount points on streams are rejected as not directories; and opening base file/stream without `FILE_OPEN_REPARSE_POINT` reports unhandled tags as expected.

## Integration Points

This file relies on `create_file`, `query_information`, `query_dir`, `set_basic_information`, `write_file_wait`, `write_ea`, `adjust_token_privileges`, and `disable_token_privileges` from the shared test harness.

## Research Notes

This file is an important map of Windows reparse compatibility requirements for WinBtrfs. The test matrix distinguishes target resolution from reparse-object access, Microsoft tags from GUID tags, file reparse points from directory reparse points, and privilege checks from ordinary access-mask checks.

## Open FIXME In File

The file ends with a missing coverage note for `FSCTL_SET_REPARSE_POINT_EX`.
