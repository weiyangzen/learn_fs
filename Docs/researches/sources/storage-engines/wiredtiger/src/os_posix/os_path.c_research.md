<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_path.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_path.c

## Purpose
Provides POSIX path semantics for absolute-path detection and path separators.

## Important APIs, Types, and Functions
`__wt_absolute_path` checks for leading `/`; `__wt_path_separator` returns `/`.

## Control Flow
Both functions are direct helpers with no allocation or error path.

## State and Persistence Behavior
No state is read or written. Their output affects how WiredTiger builds filenames under home directories.

## Dependencies and Integration Points
Used by portable path-construction code and filesystem configuration.

## Risks and Edge Cases
Relative paths beginning with other platform syntaxes are not treated as absolute on POSIX. Null path inputs are not guarded.

## Test Signals
Path utility tests should cover absolute, relative, empty, and nested POSIX paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_path.c -->
