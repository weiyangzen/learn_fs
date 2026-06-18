<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/rename.py -->
# sources/user-network-fs/blobfuse2/perf_testing/scripts/rename.py

## Purpose
Measures time to create and rename 5,000 1MiB files in a temporary folder.

## Important APIs, Types, and Functions
`create_folder` recreates the test folder. `create_files` writes zero-filled files. `rename_files` iterates directory entries and renames each file to `new_file_<i>.txt`. The script prints a JSON object with rename and create times.

## Control Flow and State
A timestamped folder under `./` is created, populated, renamed, removed, and summarized. The `output_file` variable is unused.

## Dependencies and Integration Points
Pure Python standard library. It is useful when run from a Blobfuse2 mount working directory to stress metadata-heavy create/rename operations.

## Risks and Edge Cases
The base folder is always current working directory, so accidental execution outside a test area writes 5GB locally. It is single-threaded and does not verify rename results before cleanup. Directory iteration order is filesystem-dependent but not semantically important.

## Test Signals
Single JSON line reports create and rename durations. No correctness signal remains after cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/perf_testing/scripts/rename.py -->
