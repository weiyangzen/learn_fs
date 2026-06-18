# File Research: sources/windows/winbtrfs/src/tests/ea.cpp

## Purpose

`ea.cpp` tests extended attribute support through native NT EA APIs. It validates EA buffer layout, name normalization, create-time EAs, read/write/delete/replace behavior, EA size reporting in file and directory information, `FILE_NEED_EA`, access checks, filtered reads, single-entry iteration, index-based reads, missing-EA behavior, and volume-handle rejection.

## Main Helpers

- Local `FILE_FULL_EA_INFORMATION` definition for MSVC builds.
- `ea_size()`
  - Computes aligned byte size of a `FILE_FULL_EA_INFORMATION` entry.
- `write_ea()`
  - Builds one EA entry and calls `NtSetEaFile`.
  - Supports setting the `FILE_NEED_EA` flag.
- `write_eas()`
  - Builds a chained EA buffer with `NextEntryOffset` values for multiple entries.
- `read_ea()`
  - Calls `NtQueryEaFile` without a filter and returns copied variable-size EA records.
- `create_file_ea()`
  - Wraps `NtCreateFile` and passes an EA buffer at create time.
- `check_ea_dirent<T>()`
  - Queries a directory entry and verifies filename plus `EaSize`.
- `read_eas()`
  - Builds a `FILE_GET_EA_INFORMATION` filter list and calls `NtQueryEaFile`.
  - Supports `ReturnSingleEntry`, EA index, and restart-scan behavior.

## Test Coverage

- Starts with `ea1`:
  - reading EAs on a new file returns `STATUS_NO_EAS_ON_FILE`;
  - writing `hello=world` succeeds;
  - reading returns one EA whose name is capitalized to `HELLO`;
  - `FILE_EA_INFORMATION`, `FILE_ALL_INFORMATION`, and multiple directory enumeration classes report the expected aligned EA size.
- Reopens `ea1` and adds `fOo=bar`:
  - read order contains `HELLO` then `FOO`;
  - file/all/dirent EA sizes equal the sum of both aligned entries.
- Replaces `HELLO` using mixed-case `HeLlO=baz`:
  - replacement preserves case-insensitive identity and normalized uppercase name;
  - resulting entries are `FOO=bar` and `HELLO=baz`.
- Deletes one EA by setting its value length to zero:
  - deleting `HELLO` leaves only `FOO=bar`;
  - EA size shrinks accordingly in file/all/dirent reports.
- Deletes the last EA:
  - `NtQueryEaFile` returns `STATUS_NO_EAS_ON_FILE`;
  - file/all/dirent EA sizes are zero.
- Creates `ea2`, writes two EAs in a single chained buffer, and verifies names, values, and aggregate size.
- Creates `ea3` with two create-time EAs passed to `NtCreateFile`, then verifies the resulting stored EAs and size reporting.
- Creates directory `ea4` and verifies directories can carry EAs with the same query and dirent reporting semantics as files.
- Creates `ea5`, writes an EA with `FILE_NEED_EA`, and verifies the flag is returned.
  - Opening with `FILE_NO_EA_KNOWLEDGE` is denied with `STATUS_ACCESS_DENIED`.
- Access checks:
  - a handle without `FILE_WRITE_EA` cannot write EAs;
  - a handle without `FILE_READ_EA` cannot read EAs.
- Filtered and iterative reads using `ea7`:
  - reading with a filter list returns only requested EAs in filter order;
  - `ReturnSingleEntry` returns one item;
  - with a filter list and no restart, the first filtered entry is returned again;
  - without a filter list, repeated single-entry reads advance through `HELLO`, `FOO`, and `XYZZY`, then return `STATUS_NO_MORE_EAS`;
  - an explicit EA index of 3 returns the third EA;
  - requesting a non-existent EA returns a zero-length value for the requested normalized name.
- Opens the volume root and verifies EAs are invalid on volume handles:
  - writing returns `STATUS_INVALID_PARAMETER`;
  - reading returns `STATUS_INVALID_PARAMETER`.

## Directory Information Classes Checked For `EaSize`

- `FILE_FULL_DIR_INFORMATION`
- `FILE_ID_FULL_DIR_INFORMATION`
- `FILE_BOTH_DIR_INFORMATION`
- `FILE_ID_BOTH_DIR_INFORMATION`
- `FILE_ID_EXTD_DIR_INFORMATION`
- `FILE_ID_EXTD_BOTH_DIR_INFORMATION`

## Important Dependencies

- Native EA APIs:
  - `NtSetEaFile`, `NtQueryEaFile`
- Native create API:
  - `NtCreateFile` with create-time EA buffer.
- Test harness helpers:
  - `create_file`, `query_information`, `query_all_information`, `query_dir`, `exp_status`.
- Structures:
  - `FILE_FULL_EA_INFORMATION`
  - `FILE_GET_EA_INFORMATION`
  - `FILE_EA_INFORMATION`
  - `FILE_ALL_INFORMATION`

## Notable Edge Cases

- EA names are stored/returned uppercase, and name matching is case-insensitive.
- A zero-length EA value is used as deletion, including for deleting the last EA.
- Directory-entry `EaSize` is checked only after closing the file handle; comments note dirent EA size may not update until close.
- Requesting a non-existent EA by name returns a synthetic zero-length EA record rather than failing.
- Volume handles reject EA operations.
