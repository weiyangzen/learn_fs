<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_path.c -->
# sources/storage-engines/wiredtiger/src/os_win/os_path.c

## Purpose
Provides Windows absolute-path and path-separator helpers.

## Important APIs, Types, and Functions
`__wt_absolute_path` and `__wt_path_separator`.

## Control Flow
Absolute detection recognizes drive-rooted paths like `C:\...`, drive-relative absolute-ish paths, and UNC-style leading separators. Separator returns `\`.

## State and Persistence Behavior
No state changes. Results guide filename construction under WiredTiger home directories.

## Dependencies and Integration Points
Used by portable path normalization and filesystem code before UTF-16 conversion.

## Risks and Edge Cases
Windows path grammar is broad; device paths and mixed slashes need coverage. Null/short inputs must satisfy assumptions in the implementation.

## Test Signals
Tests should cover drive paths, UNC paths, relative paths, slash variants, and empty strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_win/os_path.c -->
