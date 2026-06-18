# File Research: sources/windows/winbtrfs/src/tests/cs.cpp

## Purpose

`cs.cpp` tests per-directory case-sensitivity semantics exposed through `FileCaseSensitiveInformation`. It verifies setting/querying the case-sensitive flag, case-sensitive lookup and enumeration behavior, inherited flags, permission requirements, behavior on non-empty directories, case-collision prevention when clearing the flag, and stream-name behavior.

## Main Helpers

- `set_case_sensitive()`
  - Calls `NtSetInformationFile(FileCaseSensitiveInformation)`.
  - Sets `FILE_CS_FLAG_CASE_SENSITIVE_DIR` or clears it.
  - Verifies `IO_STATUS_BLOCK.Information` is zero.
- `create_file_cs()`
  - Local `NtCreateFile` wrapper that deliberately does not set `OBJ_CASE_INSENSITIVE`.
  - Used to distinguish object-manager case handling from filesystem directory case-sensitivity.

## Test Flow

- Creates `csdir` as a directory and sets the case-sensitive flag.
  - The comment notes Windows may return `STATUS_NOT_SUPPORTED` unless the system case-sensitivity registry setting is enabled.
- Queries `FILE_CASE_SENSITIVE_INFORMATION` and expects `FILE_CS_FLAG_CASE_SENSITIVE_DIR`.
- Creates lowercase `cs1`, records its file ID, and verifies:
  - directory enumeration by exact case succeeds;
  - enumeration by wrong case returns `STATUS_NO_SUCH_FILE`;
  - `FILE_OPEN` and `FILE_OVERWRITE` by wrong case return `STATUS_OBJECT_NAME_NOT_FOUND`.
- Creates uppercase `CS1` as a distinct file in the same directory.
  - Subsequent `FILE_OPEN_IF`, `FILE_OVERWRITE_IF`, and `FILE_SUPERSEDE` against uppercase `CS1` must operate on that uppercase inode, verified by file ID.
- Creates subdirectory `cs2` under `csdir` and verifies it inherits the case-sensitive flag.
- Creates regular file `cs3` and verifies:
  - setting the case-sensitive flag on a file returns `STATUS_INVALID_PARAMETER`;
  - querying the flag on a file returns zero.
- Tests ACL requirements for setting the flag on directory `cs5`.
  - Individual combinations missing one of `FILE_ADD_FILE`, `FILE_ADD_SUBDIRECTORY`, or `FILE_DELETE_CHILD` fail with `STATUS_ACCESS_DENIED`.
  - The combination of all three permissions succeeds.
- Tests non-empty directory behavior on `cs6`.
  - Setting, clearing, and setting the flag again on a non-empty directory succeeds while entries do not differ only by case.
  - After creating both `file` and `FILE`, clearing the flag fails with `STATUS_CASE_DIFFERING_NAMES_IN_DIR`.
- Uses `create_file_cs()` without `OBJ_CASE_INSENSITIVE` in a normal directory:
  - exact-case create/open succeeds;
  - wrong-case open is expected to return `STATUS_OBJECT_NAME_NOT_FOUND`.
- Creates an alternate data stream `cs8:stream` in a case-sensitive directory and opens it as `cs8:STREAM`.
  - The test expects this to succeed, documenting that stream-name matching remains case-insensitive here.

## Important Dependencies

- Native information class: `FileCaseSensitiveInformation`.
- Test harness helpers:
  - `create_file`, `query_information`, `query_dir`, `set_dacl`, `exp_status`.
- Windows access masks:
  - `FILE_ADD_FILE`, `FILE_ADD_SUBDIRECTORY`, `FILE_DELETE_CHILD`, `FILE_WRITE_ATTRIBUTES`, `WRITE_DAC`.

## Notable Edge Cases

- The case-sensitive directory flag may depend on Windows system policy, so this test suite assumes the environment supports it.
- Stream names are explicitly documented by the test as not following normal file-name case sensitivity.
- Clearing case sensitivity is allowed on a non-empty directory until the directory contains entries that differ only by case.
- `create_file_cs()` contains FIXME notes for root-directory, security descriptor, security quality of service, and EA-buffer variations.
