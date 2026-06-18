# sources/test-tools/crashmonkey/code/tests/rename_root_to_sub.cpp

## Purpose
`sources/test-tools/crashmonkey/code/tests/rename_root_to_sub.cpp` is a hand-written CrashMonkey test for renaming a file from the mount root into a subdirectory. It creates `/mnt/snapshot/test_file`, creates and fsyncs `/mnt/snapshot/test_dir`, writes a known `TEST_TEXT` payload with all permission bits enabled, then checkpoints immediately after `rename(old_path, new_path)`.

## Important APIs, Types, and Functions
- `rename_root_to_sub` derives from `BaseTestCase` and overrides `setup`, `run`, and `check_test`.
- `setup()` creates `TEST_DIR`, fsyncs that directory, creates `TEST_FILE` with `TEST_FILE_PERMS`, writes the static text payload, fsyncs the file, and closes it.
- `run(int checkpoint)` performs `rename(old_path.c_str(), new_path.c_str())` and returns `1` to expose the post-rename crash point.
- `check_test(...)` stats both old and new paths, classifies missing/duplicated files with `DataTestResult`, verifies the surviving object is a regular file with expected permissions, reads the payload, and compares it with `memcmp`.
- `test_case_get_instance()` and `test_case_delete_instance()` provide the dynamic-loader ABI.

## Control Flow
Setup first ensures the target subdirectory is durable by calling `mkdir`, `open(..., O_RDONLY)`, and `fsync` on the directory descriptor. It then temporarily sets `umask(0000)`, opens the old file with `O_RDWR | O_CREAT`, restores the umask, writes until the full `TEST_TEXT` length is persisted, fsyncs, and closes the file. The run phase has a single operation: rename root-level `test_file` to `test_dir/test_file`. The check phase examines old/new path existence and chooses exactly one surviving path for metadata and data validation.

## State and Persistence Behavior
Persistent state consists of one directory and one regular file under the fixed `TEST_MNT` path `/mnt/snapshot`. The setup phase makes the directory and original file durable before the tested rename, isolating crash behavior to the rename itself. After a crash at the checkpoint, acceptable recovery should have either the old file or the new file, but not neither and not both. The file type, permission mask, and byte-for-byte payload are expected to survive regardless of which pathname remains.

## Dependencies and Integration Points
This test uses raw POSIX syscalls and libc helpers rather than the generated `cm_` wrapper calls in `seq1`. It depends on `BaseTestCase`, `DataTestResult`, and the CrashMonkey loader calling setup/run/check in the expected order. It hard-codes `/mnt/snapshot` rather than using `mnt_dir_`, so it integrates only with harness setups mounted at that path.

## Risks and Edge Cases
The fixed mount path is brittle and ignores `init_values`. The private member `char text[strlen(TEST_TEXT)]` is unused and has no extra byte for a NUL terminator, though it is not referenced. `check_test()` does not free the read buffer on the successful comparison path until after validation, which is fine, but allocation size is exactly `strlen(TEST_TEXT)` and assumes byte-count comparisons only. Directory `open` uses `O_RDONLY` without `O_DIRECTORY`. The test treats both old and new files existing as `kOldFilePersisted`, which is useful for rename atomicity but may not distinguish link-count or aliasing anomalies.

## Test Signals
Strong signals are `kFileMissing`, `kOldFilePersisted`, `kFileMetadataCorrupted`, and `kFileDataCorrupted` from `DataTestResult`. A clean run should create durable setup state, expose the rename checkpoint by returning `1`, and after recovery find exactly one valid regular file containing the full `TEST_TEXT` payload with mode `0777` masked to permission bits.
