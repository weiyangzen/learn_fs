# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfile1.c

## Purpose
Provides small file-name utility operators backed by platform path helpers.

## Key Functions
- `zfile_name_combine()` combines prefix and file-name strings using `gp_file_name_combine()`.
- `zfile_name_is_absolute()` tests whether a string is an absolute path.
- `push_string()` pushes fixed strings onto the operand stack.
- `zfile_name_separator()`, `zfile_name_directory_separator()`, `zfile_name_current()`, and `zfile_name_parent()` expose platform separator/current/parent strings.

## Important Behavior
- Combination returns an integer `gp_file_name_combine_result` and the actual combined string size.
- `no_sibling` is currently hard-coded `false` for combine.
- Output strings are allocated in the current VM space.

## Research Notes
These are nonstandard convenience operators used by Ghostscript initialization/library code for portable path manipulation.
