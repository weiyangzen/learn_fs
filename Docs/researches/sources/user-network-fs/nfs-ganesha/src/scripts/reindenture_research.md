<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/reindenture -->
# sources/user-network-fs/nfs-ganesha/src/scripts/reindenture

## Purpose
`reindenture` bulk-formats C and header files under one or more directories using GNU `indent` with the project's historical formatting options. It is a developer maintenance tool rather than part of the build.

## Important APIs, Types, and Functions
The script exposes a command-line interface `reindenture dir1 [dir2 ... dirn]`. It has no shell functions. For each directory argument it runs `find <dir> -type f \( -name *.c -o -name *.h \) -print0 | xargs -0 indent ...` with a fixed option set, while `VERSION_CONTROL=simple` asks `indent` to keep simple backup files.

## Control Flow
If no arguments are provided, the script prints usage and exits nonzero. Otherwise it loops over each directory, prints a progress line, finds C/header files recursively, and pipes them to `indent`. Each directory is processed independently.

## State and Persistence Behavior
This script rewrites source files in place and may create backup files according to `indent`'s `VERSION_CONTROL=simple` behavior. It has no rollback logic and no file exclusion list.

## Dependencies and Integration Points
It depends on `/bin/sh`, `find`, `xargs`, and GNU `indent`. It integrates with the C codebase only as an external formatting pass; it is separate from checkpatch enforcement and CMake.

## Risks and Test Signals
Risks are broad formatting churn, accidental processing of vendored or generated C files, portability issues with unquoted directory names, and compatibility with non-GNU `indent` implementations. Because it uses `find $dir` unquoted, paths containing whitespace can be misparsed. Test signals are dry-run review through Git diff after running on a small directory, backup creation behavior, handling of empty directories, and shellcheck-style validation for argument quoting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/reindenture -->
