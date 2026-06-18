# sources/user-network-fs/samba/source4/torture/smb2/dir.c

## Purpose
`dir.c` implements the `smb2.dir` torture suite for SMB2 directory enumeration. It creates controlled directory trees, issues SMB2 FIND requests at multiple information levels, validates returned names and metadata against SMB2 GETINFO, exercises continuation behavior, and probes edge cases where directories are modified during enumeration. The tests are primarily about correctness of `SMB2_FIND_*` output, resume semantics, ordering assumptions, file-index behavior, scalability with large directories, and behavior while files are renamed or deleted.

## Important APIs, Types, And Functions
The file relies on Samba SMB2 client APIs from `libcli/smb2/smb2.h` and `smb2_calls.h`, raw SMB search/fileinfo unions, torture assertion helpers, talloc allocation, and `TYPESAFE_QSORT` from `lib/util/tsort.h`.

Key local types are:

- `struct file_elem`, which stores a generated filename, creation time, and a `found` flag used by enumeration validation.
- The static `levels[]` table, mapping SMB2 find information classes to raw search data levels and offsets for name and resume-key fields.
- `struct multiple_result`, a talloc-backed accumulator for non-dot search results.
- `enum continue_type`, which models the continuation modes tested by `multiple_smb2_search()`: single, file-index resume, restart, and reopen.

Important functions are:

- `populate_tree()`: removes and recreates `smb2_dir`, creates a requested number of unique files, stores their names and create times, closes and reopens the directory handle so smbd's later `readdir()` view is fresh, and returns the reopened directory handle.
- `test_find()`: validates simple enumeration with `SMB2_FIND_BOTH_DIRECTORY_INFO`, a small first response, and later larger responses. It checks that all generated files appear and that create times match the values returned by create.
- `test_fixed()`: starts enumeration on one directory handle, deletes files through a second handle, then ensures the first enumeration does not return stale deleted entries.
- `torture_single_file_search()` and `test_one_file()`: issue one-file searches for every level in `levels[]`, then compare returned fields with `RAW_FILEINFO_SMB2_ALL_INFORMATION`, alternate name info, and internal file ID information.
- `multiple_smb2_search()`: common multi-call enumeration helper that changes `continue_flags` after the first response, optionally copying the previous returned `file_index` into the next request.
- `test_many_files()`: creates 700 files and validates all information levels under all continuation modes, sorting the result client-side before comparing names.
- `test_modify_search()`: mutates attributes, deletes files, creates new names, and sets delete-on-close during a search, then restarts enumeration and checks final visibility and attributes.
- `test_sorted()`: observes whether returned names are case-insensitively sorted, but treats unsorted responses as non-fatal.
- `test_file_index()`: probes optional server support for honoring resume-by-file-index.
- `test_large_files()`: creates 2,000 files with names from 1 to 200 characters and times full enumeration.
- `test_1k_files_rename()`: repeatedly enumerates 1,000 files while renaming one file per iteration, optionally reopening the directory each iteration through the `1k_files_rename_reopendir` torture setting.
- `torture_smb2_dir_init()`: registers the suite as `dir` with tests `find`, `fixed`, `one`, `many`, `modify`, `sorted`, `file-index`, `large-files`, and `1kfiles_rename`.

## Control Flow
Most tests follow the same pattern: delete the test directory, create it with directory access, create files with `SEC_RIGHTS_FILE_ALL`, reopen the directory handle when the server-side directory stream must be refreshed, issue one or more `smb2_find_level()` calls, validate the returned `union smb_search_data` array, then close handles and remove the tree.

For single-file metadata validation, `test_one_file()` creates `torture_search.txt`, stores one response per find level in `levels[i].data`, queries the same file by handle with SMB2 GETINFO, and runs a set of field-comparison macros. The macros compare attributes, NTTIME fields, sizes, EA size, names, short name, and file IDs where the information class exposes them.

For repeated enumeration, `multiple_smb2_search()` starts with `SMB2_CONTINUE_FLAG_RESTART` unless the caller asks for reopen. It accumulates results via `fill_result()`, then sets the next continuation behavior: `SMB2_CONTINUE_FLAG_INDEX` with the last result's file index, `SMB2_CONTINUE_FLAG_SINGLE`, or no continuation flag. This helper is the center of the many-file, sorted, and rename stress tests.

The mutation tests deliberately alter server state mid-enumeration. `test_fixed()` deletes all files after beginning a search on another handle. `test_modify_search()` creates additional files, changes DOS attributes, unlinks one file, sets another file delete-on-close, restarts enumeration, and checks the final directory contents. `test_1k_files_rename()` turns this into a repeated stress pattern, validating that every enumeration still maps cleanly to the current expected `fname_list`.

## State And Persistence Behavior
The remote persistent state is confined to the `smb2_dir` test directory and test files under it. Each test starts with `smb2_deltree(tree, DNAME)` or equivalent cleanup and ends by closing handles and deleting the tree. Directory handles are intentionally closed and reopened in `populate_tree()` and `test_large_files()` to make sure later enumeration sees the freshly created entries through smbd's directory stream.

Client-side state is talloc-scoped. `levels[]` is file-static and stores per-level search data for `test_one_file()`, so it is reused across invocations but refreshed before comparison. `compare_data_level` and `level_sort` are file-static globals used by the qsort comparator; this design is fine for serial torture execution but not reentrant. `struct multiple_result` owns a growing `union smb_search_data` array under its `tctx`.

The tests distinguish hard protocol requirements from optional server behavior. Sorted directory order and honoring file-index resume are reported as informational when unsupported, not as failures. Windows NTFS behavior around zero file indices is explicitly treated as a skip for the file-index test.

## Dependencies
The file depends on SMB2 create, close, unlink, set attribute, setinfo, getinfo, directory find, tree cleanup, and test-directory helpers. It also depends on Samba string and time utilities such as `generate_unique_strs()`, `generate_random_str()`, `nt_time_string()`, `timespec_elapsed2()`, `strcasecmp_m()`, and `strcmp_safe()`.

The search-level machinery depends on the shape of `union smb_search_data` and the `RAW_SEARCH_DATA_*` enum remaining aligned with the corresponding `SMB2_FIND_*` levels. The offset-based `extract_name()` helper is sensitive to structure layout changes. The rename stress test depends on `RAW_SFILEINFO_RENAME_INFORMATION` via `smb2_setinfo_file()`.

## Integration Points
`torture_smb2_dir_init()` is added into the top-level SMB2 torture suite from `smb2.c`, exposing these tests as `smb2.dir.*`. The exported helper `torture_single_file_search()` is non-static and can be reused by other torture code that needs one-file SMB2 search validation.

The tests exercise server directory enumeration paths, filename normalization/case behavior, DOS attribute mapping, file ID and alternate-name reporting, allocation and timestamp propagation, and handling of directory stream invalidation after mutation. Results are useful for Samba server changes in smbd directory listing, VFS backends, durable directory handles, and metadata mapping.

## Risks
The file contains two suspicious missing-file validation loops: both `test_find()` and `test_large_files()` iterate `i` but check `files[j].found` and report `files[j].name`. Because `j` is reused from earlier inner loops, this can mask or misreport missing entries. This is a test-code risk rather than a production-server risk.

`extract_name()` uses `memcpy()` from a computed offset into a union to recover a `char *`; this is compact but fragile if the union layout changes or if a level is paired with the wrong `data_level`. `multiple_smb2_search()` returns failure when a response has zero entries or the accumulated result is empty, which can make unusual but legal empty responses hard to distinguish from protocol errors. The global qsort state means the comparator is not thread-safe.

Performance-oriented tests create 700, 1,000, or 2,000 files and can be slow on high-latency shares or backends with expensive directory operations. Cleanup is best-effort; a process abort can leave `smb2_dir` behind. Some tests assume create-time stability and attribute semantics that may vary across filesystem backends.

## Test Signals
Strong pass signals are exact file counts including `.` and `..` where expected, successful comparison of every find information class against SMB2 GETINFO, stable behavior after deletion or attribute mutation, and no missing/extra names in large enumerations. Informational signals include comments about unsorted directory listings and skipped file-index resume when the server returns zero file indices.

Regression-sensitive outputs include `STATUS_NO_MORE_FILES` termination, `NT_STATUS_OK` on all create/find/getinfo/setinfo operations, correct `FILE_ATTRIBUTE_HIDDEN`, `FILE_ATTRIBUTE_SYSTEM`, `FILE_ATTRIBUTE_ARCHIVE`, and `FILE_ATTRIBUTE_NORMAL` visibility in `test_modify_search()`, and successful repeated rename/enumerate loops in `1kfiles_rename`.
