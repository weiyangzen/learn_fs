# File Research: sources/windows/winbtrfs/src/tests/test.cpp

## Purpose

`test.cpp` is the shared executable harness for the WinBtrfs filesystem behavior tests. It provides low-level NT wrappers, result reporting, filesystem detection, test dispatch, temporary test directory setup, and process-token privilege control.

## Main Facilities

- Global `enum fs_type fstype`: records detected filesystem type as unknown, NTFS, or Btrfs.
- `create_file(...)`: wraps `NtCreateFile`, verifies returned `iosb.Information`, and returns `unique_handle`.
- `query_all_information(...)`: two-step `FileAllInformation` query with dynamic name buffer sizing.
- `query_information<T>(...)`: template mapping C++ result types to `FILE_INFORMATION_CLASS`, with explicit instantiations.
- `query_dir<T>(...)`: template wrapper for `NtQueryDirectoryFile` across multiple directory information classes.
- `test(...)`: runs one test lambda, catches exceptions, prints PASS/FAIL, and updates counters.
- `exp_status(...)`: asserts that a callable throws the expected NTSTATUS, or succeeds when expected status is `STATUS_SUCCESS`.
- `query_file_name_information(...)`: dynamic `FileNameInformation` or `FileNormalizedNameInformation` query.
- `disable_token_privileges(...)`: disables all privileges in the supplied token.
- `u16string_to_string(...)`: converts UTF-16 test names/messages for output.
- `do_tests(...)`: dispatches named tests or `all`.
- `fs_driver_path(...)`: uses `FileFsDriverPathInformation` to detect whether NTFS or WinBtrfs is in the stack.
- `get_driver_path(...)`, `get_version(...)`, `driver_string(...)`: report driver binary and version.
- `wmain(...)`: command-line entrypoint.

## Test Dispatch

`do_tests` opens the process token with adjustment/query/duplicate rights, disables privileges, then dispatches the suite by name. Registered tests include create, supersede, overwrite, open-by-ID, I/O, mmap, rename, rename_ex, delete, links, oplocks, case sensitivity, reparse, streams, EA, fileinfo, and security.

For each selected test group it prints `Running test <name>`, resets per-group counters, invokes the function, and prints `Passed X/Y`. For `all`, it also prints a total summary.

## Directory and Filesystem Setup

`wmain` accepts either `<dir>` or `<test> <dir>`, strips trailing backslashes, converts the path to an NT `\??\...` path, appends a timestamp child directory, and creates that directory as the test root.

Filesystem type detection avoids `FileFsAttributeInformation` and instead checks whether `\FileSystem\NTFS` or `\Driver\btrfs` appears in the driver path for the test root. The result controls conditional expectations in files such as `rename.cpp` and `streams.cpp`.

## Query Helper Details

`query_dir<T>` supports `FILE_DIRECTORY_INFORMATION`, `FILE_BOTH_DIR_INFORMATION`, `FILE_FULL_DIR_INFORMATION`, ID variants, extended ID variants, `FILE_NAMES_INFORMATION`, and `FILE_REPARSE_POINT_INFORMATION`. It aligns the query buffer to 8 bytes, handles `STATUS_BUFFER_OVERFLOW` for variable-length directory records, and copies each returned record into stable `varbuf<T>` storage.

`query_information<T>` maps many file information types used across the test suite, including stat, LX stat, attribute tag, compression, network open, standard link, file ID, and standard information extended aliases.

## Research Notes

This harness defines the contract used by all listed test files. Its strict `iosb.Information` checks, exact NTSTATUS assertions, and filesystem-type conditional behavior make the suite useful as a compatibility oracle rather than a loose smoke test.

## Open FIXMEs In File

The harness notes future coverage for synchronous I/O access requirements, opening with `RootDirectory`, directory querying variants, notifications, IOCTL/FSCTL coverage, volume information, volume labels, locking, object IDs, IO completions, share access, reflinks, subvolumes, snapshots, send/receive, and Linux/Windows concept mapping.
