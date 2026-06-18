# File Research: sources/windows/winbtrfs/src/tests/overwrite.cpp

## Purpose

This is the WinBtrfs user-mode overwrite disposition conformance test. It checks `FILE_OVERWRITE` and `FILE_OVERWRITE_IF` behavior for missing files, readonly/hidden/system attributes, open handles, directories, case preservation, and create-vs-overwrite result reporting.

The single entry point is `test_overwrite(const u16string& dir)`, declared in `src/tests/test.h` and registered in `src/tests/test.cpp` under the test name `overwrite`.

## Test Coverage

The test verifies these cases:

- Overwriting a non-existent file with `FILE_OVERWRITE` fails with `STATUS_OBJECT_NAME_NOT_FOUND`.
- Overwriting a readonly file fails with `STATUS_ACCESS_DENIED`.
- Overwriting an already-open file can succeed when sharing allows it.
- A normal file can be overwritten and reopened with `FILE_OVERWRITTEN`.
- Overwrite can add the readonly attribute.
- Overwriting a file while changing it into a directory is rejected with `STATUS_INVALID_PARAMETER`.
- Overwrite can add the hidden attribute.
- Clearing hidden through overwrite is rejected with `STATUS_ACCESS_DENIED`.
- Adding the system attribute is allowed when hidden remains set.
- Clearing system through overwrite is rejected with `STATUS_ACCESS_DENIED`.
- Overwriting a directory as a directory is rejected with `STATUS_INVALID_PARAMETER`.
- Overwriting a directory while requesting a non-directory file is rejected with `STATUS_FILE_IS_A_DIRECTORY`.
- Overwriting with a different path case opens the existing file but preserves the original on-disk name casing; the test checks the returned name still ends with `\overwrite3`.
- `FILE_OVERWRITE_IF` creates a file when it does not exist and overwrites it when it does exist.

## Dependencies And Side Effects

The file uses the shared test harness from `test.h`:
- `test` for named test steps
- `exp_status` for expected NTSTATUS failures
- `create_file` for native-style create/open operations
- `query_file_name_information` for final name casing verification
- `unique_handle` for handle lifetime management

It creates files/directories under the supplied test directory with names including `nonsuch`, `overwritero`, `overwrite`, `overwrite2`, `overwritedir`, `overwrite3`, and `overwriteif`.

## Notable Observations

This file is compact and focused. It complements broader create/supersede tests by isolating overwrite-specific Windows semantics, especially attribute-protection behavior and case-preserving lookup behavior on case-insensitive opens.
