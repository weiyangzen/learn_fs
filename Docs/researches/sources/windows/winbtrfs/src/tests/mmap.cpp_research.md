# File Research: sources/windows/winbtrfs/src/tests/mmap.cpp

## Purpose

`mmap.cpp` is the WinBtrfs user-mode integration test coverage for Windows section objects and memory-mapped file behavior. It validates how the filesystem interacts with `NtCreateSection`, `NtMapViewOfSection`, cache coherency, file locks, truncation, delete disposition, rename/link replacement, and `SEC_IMAGE` image-section restrictions.

It also provides helper routines used by other tests, notably `create_section` and `pe_image`, which `links.cpp` uses for mapped-image hardlink replacement checks.

## Helper Functions

- `create_section` wraps `NtCreateSection`, optionally passing a maximum section size. It returns a `unique_handle` or throws the underlying NTSTATUS.
- `map_view` wraps `NtMapViewOfSection`, accepts `STATUS_IMAGE_NOT_AT_BASE` as success, and returns the mapped address.
- `unmap_view` wraps `NtUnmapViewOfSection`.
- `lock_file` wraps `NtLockFile` for byte-range lock setup.
- `align` rounds sizes up to a specified alignment.
- `pe_image` synthesizes a minimal 32-bit PE image containing one `.data` section populated with caller-provided bytes. The generated image has DOS headers, NT headers, section headers, `FILE_ALIGNMENT` of `0x200`, and `SECTION_ALIGNMENT` of `0x1000`.

## Basic Section Creation Tests

`test_mmap` begins with negative section creation cases:

- Creating a committed section on an empty file must fail with `STATUS_MAPPED_FILE_SIZE_ZERO`.
- Creating a section on a directory must fail with `STATUS_INVALID_FILE_FOR_SECTION`.
- Creating a section larger than the file must fail with `STATUS_SECTION_TOO_BIG`.
- Creating a read-write section through a handle lacking `FILE_WRITE_DATA` must fail with `STATUS_ACCESS_DENIED`.

These cases validate WinBtrfs dispatch and cache-manager integration around section-object creation constraints.

## Data Mapping and Cache Coherency

The test validates coherency in both directions:

- Writes random data to a file, creates a read-only section, maps it, and verifies the mapped bytes match file contents.
- Writes a new integer through normal file I/O and verifies the existing mapping observes the updated value.
- Creates a read-write mapping, writes through the mapped view, and verifies normal file reads observe the mapped write.

These scenarios exercise the filesystem's cached I/O path, section object pointers, and data synchronization between `read_file`/`write_file` and mapped views.

## Locking, Size, Delete, and Replacement Semantics

The test covers non-image mapped-file behavior:

- A byte-range lock does not prevent creating and mapping a section over the locked file.
- Extending a file that already has a section succeeds.
- Truncating or clearing a file with an active data section fails with `STATUS_USER_MAPPED_FILE`.
- Marking a mapped file delete-pending fails with `STATUS_CANNOT_DELETE`.
- A file already marked delete-pending can still have a section created and mapped while its handle remains open.
- A mapped non-image file can be replaced by rename.
- A mapped non-image file can be replaced by hardlink.

The rename and link replacement cases distinguish normal data sections from image sections: data mappings are allowed to survive namespace replacement, while image mappings receive stricter protection.

## Image Section Tests

The test creates synthetic PE files with `pe_image` and maps them as `SEC_IMAGE` sections.

Image mapping behavior:

- Mapping a `SEC_IMAGE` section succeeds.
- The mapped `.data` payload appears at virtual address offset `0x1000`, matching the generated section alignment.
- Truncating a mapped image to zero fails with `STATUS_USER_MAPPED_FILE`.
- Extending the mapped image file succeeds.
- Truncating it back to the original size while still mapped fails with `STATUS_USER_MAPPED_FILE`.

Image-section replacement and deletion protections:

- Overwriting a mapped image with `FILE_OVERWRITE` fails with `STATUS_SHARING_VIOLATION`.
- Replacing a mapped image by rename fails with `STATUS_ACCESS_DENIED`.
- Deleting a mapped image fails with `STATUS_CANNOT_DELETE`.
- Replacing a mapped image by hardlink fails with `STATUS_ACCESS_DENIED`.

These tests ensure WinBtrfs cooperates with Windows memory manager image-section rules and does not permit namespace or size mutations that would invalidate mapped executable images.

## Dependencies and Cross-File Interactions

This file depends on shared test harness helpers from `test.h`, including:

- File helpers: `create_file`, `set_end_of_file`, `set_disposition_information`, `set_rename_information`, `set_link_information`.
- I/O helpers: `write_file`, `read_file`, `random_data`.
- Assertion helpers: `test`, `exp_status`, `formatted_error`, `ntstatus_error`.
- Handle wrapper: `unique_handle`.

It interacts with behavior implemented in WinBtrfs read/write, cache-manager, file-size, disposition, rename, and hardlink paths. It also exports practical helper coverage to `links.cpp`, where mapped-image hardlink replacement is tested through `pe_image` and `create_section`.

## Edge Cases and Risks

- `map_view` treats `STATUS_IMAGE_NOT_AT_BASE` as success, which is correct for image mappings but means callers must rely on the returned address rather than an expected preferred image base.
- The synthetic PE image is deliberately minimal; it is enough for `SEC_IMAGE` tests but is not a general executable generator.
- The tests distinguish data-section replacement from image-section replacement. That distinction is easy to regress in filesystem rename/link/disposition code if all mapped files are handled uniformly.
- Truncation checks cover both zero-length truncation and truncation back to the originally mapped image size after extension, catching stale section-size assumptions.

## Research Summary

`mmap.cpp` is the WinBtrfs regression suite for NT section object behavior. It verifies section creation error codes, mapped-view data coherency, allowed extension versus forbidden truncation, delete-disposition protection, rename/link replacement semantics for mapped data files, and strict protection for mapped image files. The file is central test coverage for WinBtrfs integration with the Windows Cache Manager and Memory Manager.
