# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfile1.c

## Purpose
Provides small file-name utility operators backed by platform path helpers.

## Key Functions
- `zfile_name_combine()` combines prefix and file-name strings using `gp_file_name_combine()`.
- `zfile_name_is_absolute()` tests whether a string is an absolute path.
- `zfile_name_separator()`, `zfile_name_directory_separator()`, `zfile_name_current()`, and `zfile_name_parent()` expose platform path constants.

## Important Behavior
- Combination returns a `gp_file_name_combine_result` plus the actual combined string.
- Output strings are allocated in the current VM space.

## Research Notes
Nonstandard convenience operators for portable path manipulation.
