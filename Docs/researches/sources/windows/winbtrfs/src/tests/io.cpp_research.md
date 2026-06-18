# File Research: sources/windows/winbtrfs/src/tests/io.cpp

## Purpose

`io.cpp` tests WinBtrfs file I/O semantics through native NT reads, writes, file-position state, allocation size, EOF, valid-data length, no-intermediate-buffering alignment, append-only writes, asynchronous event-backed I/O, and `FSCTL_SET_ZERO_DATA`.

The file also provides shared helper routines used by other tests, including token privilege adjustment, random data generation, read/write wrappers, event creation, allocation/EOF/VDL setters, and zeroing.

## Main Helpers

- `adjust_token_privileges()`
  - Calls `NtAdjustPrivilegesToken` for one privilege.
  - Used here for `SeManageVolumePrivilege` and by other test files for traverse privilege.
- `set_allocation()`
  - Calls `NtSetInformationFile(FileAllocationInformation)`.
- `random_data()`
  - Fills a vector with random 32-bit words.
- `write_file()`
  - Synchronous `NtWriteFile` wrapper.
  - Optional explicit offset; verifies byte count in `IO_STATUS_BLOCK.Information`.
- `create_event()`
  - Creates a notification event for pending I/O completion.
- `write_file_wait()`
  - Event-backed write wrapper that handles `STATUS_PENDING`.
- `read_file()`
  - Synchronous `NtReadFile` wrapper that returns exactly the bytes reported by the I/O status block.
- `read_file_wait()`
  - Event-backed read wrapper that handles `STATUS_PENDING`.
- `set_position()`
  - Calls `NtSetInformationFile(FilePositionInformation)`.
- `set_valid_data_length()`
  - Calls `NtSetInformationFile(FileValidDataLengthInformation)`.
- `set_end_of_file()`
  - Calls `NtSetInformationFile(FileEndOfFileInformation)`.
- `set_zero_data()`
  - Issues `FSCTL_SET_ZERO_DATA` through `NtFsControlFile`, with event wait for pending completion.

## Shared `write_check()` Coverage

`test_io()` defines a reusable `write_check(multiple, sector_align)` block used for normal and no-intermediate-buffering files.

It verifies:

- writing random data advances the current file pointer to EOF;
- allocation size is at least the written size and EOF equals written size;
- `FILE_COMPRESSION_INFORMATION.CompressedFileSize` equals the data size;
- reads at EOF and beyond EOF return `STATUS_END_OF_FILE` without moving the file pointer;
- negative file positions are rejected with `STATUS_INVALID_PARAMETER`;
- reading the full file from position zero returns exact data and advances position;
- reads that cross EOF return only available bytes;
- extending EOF creates zero-filled ranges;
- valid data length cannot be set to zero or past EOF;
- valid data length can be set to EOF when `SeManageVolumePrivilege` is enabled;
- truncating EOF preserves the prefix and adjusts position/standard information.

When `sector_align` is true, it additionally expects unbuffered alignment enforcement:

- reads smaller than a sector fail;
- odd/unaligned file positions fail;
- reads past EOF use sector-sized alignment.

## `test_io()` Coverage

- Enables `SeManageVolumePrivilege` at the start because setting valid data length requires it.
- Creates `io` and runs `write_check(4096, false)`.
- Creates `ioshort` and runs `write_check(200, false)` to cover short non-sector-aligned ordinary I/O.
- Disables privileges and verifies setting valid data length without privilege returns `STATUS_PRIVILEGE_NOT_HELD`.
- Allocation-size behavior:
  - `ioalloc`: setting allocation to 4096 changes allocation but not EOF; writing 4096 bytes sets EOF; setting allocation to zero truncates allocation and EOF to zero.
  - `ioprealloc`: create-time allocation size of 4096 is reported while EOF remains zero; after writing, EOF becomes 4096; setting allocation to zero clears both.
  - directories reject EOF and allocation changes with `STATUS_INVALID_PARAMETER`.
  - create-time allocation for a directory is ignored; allocation and EOF remain zero.
- File-pointer special offset behavior on synchronized handle `io3`:
  - explicit offset reads still update current file position;
  - `FILE_USE_FILE_POINTER_POSITION` reads/writes use and advance the file pointer;
  - `FILE_WRITE_TO_END_OF_FILE` appends and advances the pointer;
  - using `FILE_WRITE_TO_END_OF_FILE` for reads returns `STATUS_INVALID_PARAMETER`;
  - final contents verify overwrite/append placement.
- Non-synchronized handle behavior on `io4`:
  - I/O without an explicit offset fails with `STATUS_INVALID_PARAMETER`;
  - explicit-offset write/read does not move file position;
  - `FILE_USE_FILE_POINTER_POSITION` is invalid;
  - `FILE_WRITE_TO_END_OF_FILE` appends successfully without moving the stored file pointer;
  - event-backed wait helpers are used for this path.
- `FILE_APPEND_DATA` behavior on `io5`:
  - writes append even when an explicit offset is supplied;
  - position advances to the new EOF after each write;
  - final contents confirm all writes were appended in order.
- No-intermediate-buffering behavior on `io6`:
  - creates with `FILE_NO_INTERMEDIATE_BUFFERING`;
  - runs `write_check(4096, true)`;
  - writes shorter than a sector fail;
  - odd positions fail;
  - reads shorter than a sector fail;
  - setting EOF to an odd value is allowed, then setting to 4096 restores sector-sized EOF.
- Zero-data behavior:
  - `io7`: writes 150 random bytes, zeros byte range `[25, 125)`, and verifies only that range changed to zero.
  - `io8`: writes three sectors, zeros the middle sector, and verifies the middle sector is zero while surrounding sectors remain unchanged.

## Important Dependencies

- Native I/O APIs:
  - `NtReadFile`, `NtWriteFile`, `NtCreateEvent`, `NtWaitForSingleObject`, `NtFsControlFile`
  - `NtSetInformationFile` with allocation, position, valid-data-length, and EOF classes
- Privileges:
  - `SE_MANAGE_VOLUME_PRIVILEGE`
- Test harness helpers:
  - `create_file`, `query_information`, `disable_token_privileges`, `exp_status`
- Windows flags:
  - `FILE_SYNCHRONOUS_IO_NONALERT`
  - `FILE_NO_INTERMEDIATE_BUFFERING`
  - `FILE_APPEND_DATA`
  - `FILE_USE_FILE_POINTER_POSITION`
  - `FILE_WRITE_TO_END_OF_FILE`

## Notable Edge Cases

- Synchronous handles and non-synchronous handles have different file-pointer rules; this file explicitly tests both.
- Append-only access overrides explicit write offsets.
- Unbuffered I/O rejects unaligned buffer lengths and positions, but EOF itself can temporarily be set to a non-sector value.
- Setting allocation size to zero is expected to truncate EOF to zero.
- `FSCTL_SET_ZERO_DATA` is tested for both byte-granular and sector-granular ranges.
- DASD I/O is listed as a FIXME and is not covered.
