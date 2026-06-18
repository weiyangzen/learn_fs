# File Research: sources/windows/winbtrfs/src/tests/fileinfo.cpp

## Purpose

`fileinfo.cpp` tests `FileBasicInformation` set/query behavior for timestamps and attributes. It verifies Windows sentinel timestamp semantics, automatic timestamp updates after writes, access requirements for reading/writing basic information, and attribute normalization for files versus directories.

## Main Helper

- `set_basic_information()`
  - Calls `NtSetInformationFile(FileBasicInformation)`.
  - Sets creation, last-access, last-write, change time, and file attributes.
  - Verifies success and zero `IO_STATUS_BLOCK.Information`.

## Test Coverage

- Creates `fileinfo1` with synchronized I/O, read/write attributes, and write-data access.
- Captures initial `FILE_BASIC_INFORMATION` and expects default file attributes to be `FILE_ATTRIBUTE_ARCHIVE`.
- Calls `set_basic_information()` with all times and attributes set to zero.
  - Expects zero fields to leave existing times and attributes unchanged.
- Writes data after a short delay and verifies:
  - creation time is unchanged;
  - last-write time changes;
  - change time changes;
  - attributes are unchanged.
- Tests timestamp sentinel values:
  - setting `LastWriteTime` to `-1` suppresses last-write updates on the next write while change time still changes.
  - setting `ChangeTime` to `-1` preserves both last-write and change time on the next write in the asserted behavior.
  - setting `LastWriteTime` to `-2` re-enables last-write update while preserving change time for the next write.
  - setting `ChangeTime` to `-2` re-enables both last-write and change-time updates.
- Sets explicit timestamp value `128790414900000000` and verifies:
  - `CreationTime` can be set to that value and causes change time to update;
  - `LastWriteTime` can be set to that value and causes change time to update;
  - `ChangeTime` can be set to that value exactly.
- Access checks:
  - opening without `FILE_READ_ATTRIBUTES` and querying basic information returns `STATUS_ACCESS_DENIED`;
  - opening without `FILE_WRITE_ATTRIBUTES` and setting basic information returns `STATUS_ACCESS_DENIED`.
- File attribute normalization on `fileinfo1`:
  - setting hidden yields exactly `FILE_ATTRIBUTE_HIDDEN`;
  - setting normal yields exactly `FILE_ATTRIBUTE_NORMAL`;
  - setting normal plus readonly yields exactly `FILE_ATTRIBUTE_READONLY`;
  - setting directory on a file fails with `STATUS_INVALID_PARAMETER`;
  - setting reparse-point or sparse-file attributes is ignored, leaving normal attributes.
- Directory attribute normalization on `fileinfo2`:
  - setting hidden yields `FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_HIDDEN`;
  - setting normal yields `FILE_ATTRIBUTE_DIRECTORY`;
  - setting normal plus readonly yields `FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_READONLY`;
  - setting directory alone preserves `FILE_ATTRIBUTE_DIRECTORY`;
  - setting reparse-point or sparse-file is ignored, leaving directory attributes.

## Important Dependencies

- Native API:
  - `NtSetInformationFile(FileBasicInformation)`
- Test harness helpers:
  - `create_file`, `query_information`, `write_file`, `exp_status`
- Time behavior:
  - Uses `NtDelayExecution` with a 100 ms delay to make timestamp changes observable.

## Notable Edge Cases

- Last access time is mostly ignored because the Windows `NtfsDisableLastAccessUpdate` policy can make it unpredictable.
- The test assumes NT-style sentinel values `-1` and `-2` for timestamp update suppression/re-enabling.
- File and directory attribute rules differ: directories always retain `FILE_ATTRIBUTE_DIRECTORY`, while files reject attempts to become directories via basic-information attributes.
- Reparse-point and sparse-file attributes are ignored when set through this path.
