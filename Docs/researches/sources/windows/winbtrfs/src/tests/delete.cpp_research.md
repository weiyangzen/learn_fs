# File Research: sources/windows/winbtrfs/src/tests/delete.cpp

## Purpose

`delete.cpp` tests Windows delete disposition semantics for WinBtrfs. It covers classic `FileDispositionInformation`, extended `FileDispositionInformationEx`, delete-pending visibility, directory removal, share-delete behavior, alternate data streams, `FILE_DELETE_ON_CLOSE`, readonly handling, mapped image-section deletion checks, POSIX delete semantics, and hardlink/link-count reporting.

## Main Helpers

- `set_disposition_information()`
  - Calls `NtSetInformationFile(FileDispositionInformation)` with `FILE_DISPOSITION_INFORMATION.DoDeleteFile`.
  - Verifies success and zero `IO_STATUS_BLOCK.Information`.
- `set_disposition_information_ex()`
  - Calls `NtSetInformationFile(FileDispositionInformationEx)` with `FILE_DISPOSITION_INFORMATION_EX.Flags`.
  - Used for modern flags such as POSIX semantics, force image-section check, ignore readonly, and on-close control.

## `test_delete()` Coverage

This function exercises classic disposition and `FILE_DELETE_ON_CLOSE`.

- Deletes a file through classic disposition:
  - entry remains visible while the deleting handle is open;
  - `FILE_STANDARD_INFORMATION.DeletePending` becomes true;
  - `FILE_STANDARD_LINK_INFORMATION.NumberOfAccessibleLinks` becomes zero while total links remains one;
  - entry disappears after handle close.
- Deletes an empty directory with equivalent visibility/delete-pending checks.
- Tries to delete a non-empty directory:
  - deleting the directory fails with `STATUS_DIRECTORY_NOT_EMPTY`;
  - even after marking the child file for deletion, the directory remains non-empty until the child handle closes;
  - after the child closes, directory deletion succeeds.
- Tests clearing a pending delete:
  - marking a file delete-pending prevents reopen with `STATUS_DELETE_PENDING`;
  - clearing the flag restores normal standard/link information and allows reopen.
- Tests multiple handles:
  - deletion waits until all open handles close;
  - directory entry remains after the first handle closes and disappears after the second closes.
- Confirms `DELETE` access is required; setting delete disposition without it returns `STATUS_ACCESS_DENIED`.
- Tests a file with an alternate data stream:
  - marking the unnamed stream/file delete-pending also makes the ADS handle delete-pending;
  - clearing disposition on the stream is ignored;
  - deletion completes only after both file and stream handles close.
- Tests `FILE_DELETE_ON_CLOSE` on a file:
  - delete-pending is not reported immediately;
  - the entry disappears when the handle closes.
- Tests `FILE_DELETE_ON_CLOSE` plus a second share-delete handle:
  - opening without `FILE_SHARE_DELETE` fails;
  - opening with share-delete succeeds;
  - closing the first handle makes the second handle report delete-pending;
  - clearing delete disposition on the second handle restores accessible link reporting and leaves the file present after close.
- Tests readonly behavior:
  - opening a readonly file with `FILE_DELETE_ON_CLOSE` returns `STATUS_CANNOT_DELETE`;
  - setting disposition on a readonly file returns `STATUS_CANNOT_DELETE`.
- Tests directories with `FILE_DELETE_ON_CLOSE`:
  - an empty directory is removed at close;
  - a directory made non-empty before close remains present.

## `test_delete_ex()` Coverage

This function repeats core delete behavior with extended disposition flags and adds newer semantics.

- `FILE_DISPOSITION_DELETE` mirrors classic delete behavior for files and directories:
  - entry remains visible until close;
  - delete-pending and accessible-link counts update while open.
- Clearing with `FILE_DISPOSITION_DO_NOT_DELETE` restores normal reopen behavior.
- Multiple-handle deletion again waits until the last handle closes.
- Mapped image-section behavior:
  - creates a PE-like image file, maps it with `SEC_IMAGE`, and tries delete disposition;
  - with one link, deletion with or without `FILE_DISPOSITION_FORCE_IMAGE_SECTION_CHECK` fails with `STATUS_CANNOT_DELETE`;
  - after adding a hardlink, deletion with force-image-section check still fails, but deletion without that flag succeeds.
- Readonly extended deletion:
  - `FILE_DISPOSITION_DELETE` fails on a readonly file with `STATUS_CANNOT_DELETE`;
  - adding `FILE_DISPOSITION_IGNORE_READONLY_ATTRIBUTE` succeeds.
- POSIX delete semantics:
  - enables `SeChangeNotifyPrivilege` to query hard links;
  - creates two handles to the same file;
  - `FILE_DISPOSITION_DELETE | FILE_DISPOSITION_POSIX_SEMANTICS` makes link count zero and delete-pending true;
  - the original directory entry is still visible until the deleting handle closes;
  - after close, the remaining handle is an orphaned inode whose name and hardlink parent/name no longer match the original directory entry;
  - reopening by the original name returns `STATUS_OBJECT_NAME_NOT_FOUND`.
- Extended on-close flags:
  - for a file opened with `FILE_DELETE_ON_CLOSE`, `FILE_DISPOSITION_DO_NOT_DELETE | FILE_DISPOSITION_ON_CLOSE` cancels delete-on-close and the entry remains after close.
  - trying to set delete-on-close on a handle not originally opened that way returns `STATUS_NOT_SUPPORTED`.
  - explicitly setting `FILE_DISPOSITION_DELETE | FILE_DISPOSITION_ON_CLOSE` on a delete-on-close handle is accepted.

## Important Dependencies

- Native file information classes:
  - `FileDispositionInformation`, `FileDispositionInformationEx`
  - `FILE_STANDARD_INFORMATION`, `FILE_STANDARD_LINK_INFORMATION`
- Test helpers:
  - `create_file`, `query_dir`, `query_information`, `query_file_name_information`, `query_links`
  - `set_link_information`, `write_file`, `create_section`, `pe_image`
  - `adjust_token_privileges`, `disable_token_privileges`
- Windows flags:
  - `FILE_DELETE_ON_CLOSE`
  - `FILE_DISPOSITION_DELETE`, `FILE_DISPOSITION_DO_NOT_DELETE`
  - `FILE_DISPOSITION_POSIX_SEMANTICS`
  - `FILE_DISPOSITION_FORCE_IMAGE_SECTION_CHECK`
  - `FILE_DISPOSITION_IGNORE_READONLY_ATTRIBUTE`
  - `FILE_DISPOSITION_ON_CLOSE`

## Notable Edge Cases

- Directory entries remain visible while a delete-pending handle is still open for ordinary delete semantics.
- Link reporting distinguishes accessible links from total links; delete-pending files can have zero accessible links while total links remains one.
- Delete-on-close state is not the same as immediate delete-pending state; several tests assert it is not reported until the relevant handle closes.
- POSIX delete moves the remaining open handle to orphaned naming state instead of keeping the original visible path.
- Mapped image-section deletion behavior depends on link count and `FILE_DISPOSITION_FORCE_IMAGE_SECTION_CHECK`.
- A comment in one test says clearing delete disposition on the second handle is ignored, but the following assertions expect delete-pending to become false and accessible links to return to one; the behavior being asserted is the authoritative contract for the test.
