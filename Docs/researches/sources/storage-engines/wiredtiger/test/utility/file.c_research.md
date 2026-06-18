# sources/storage-engines/wiredtiger/test/utility/file.c

## Purpose

`file.c` is the shared filesystem helper implementation for WiredTiger tests. It provides recursive copy, fast copy, move, mkdir, recursive remove, existence checks, and sentinel file creation across Unix and Windows.

## Important APIs, Types, and Functions

Internal types are `file_info_t`, `file_callback_t`, and `copy_data`. Internal workers include `process_directory_tree`, `copy_on_file`, `copy_on_directory_enter`, `copy_on_directory_leave`, `remove_on_file`, and `remove_on_directory_leave`. Exports include `testutil_copy`, `testutil_copy_fast`, `testutil_move`, `testutil_copy_ext`, `testutil_mkdir`, `testutil_mkdir_ext`, `testutil_recreate_dir`, `testutil_remove`, `testutil_exists`, and `testutil_sentinel`.

## Control Flow

The core traversal function recursively stats/list directories and invokes callbacks for files and directory entry/leave. Copy helpers expand glob patterns, create destination directories when needed, copy regular files with buffered `pread`/`write` or Windows `CopyFileA`, optionally preserve timestamps, and optionally hard-link subtrees. Remove helpers traverse leaves before directories.

## State and Persistence Behavior

The file manipulates real filesystem state: copied trees, hard links, timestamps, created directories, removed paths, and empty sentinel files. It treats missing paths as acceptable for glob-style remove/copy no-match cases where configured.

## Dependencies and Integration Points

Depends on `test_util.h`, POSIX/Windows filesystem APIs, `glob`, `dirname`/`basename`, `utime`/`utimes`, process helpers for `cp`, and testutil assertion/error wrappers.

## Risks and Edge Cases

Only regular files are copied; special files are silently ignored. `testutil_copy_fast` shells out to `cp -R -p` on Unix, so behavior depends on system `cp`. Hard-link mode tracks depth based on matching prefixes and can share storage unexpectedly if misused.

## Test Signals

Signals are exact copied/removable directory trees, preserved timestamps when requested, successful recursive parent creation, ENOENT-safe existence checks, and sentinel file presence.
