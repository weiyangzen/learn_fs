# sources/storage-engines/wiredtiger/test/ctest_dir_sync.cmake

## Purpose
This CMake script synchronizes immediate files from a source directory to a destination directory for test runtime assets.

## Important APIs, Types, and Functions
- Requires `SYNC_DIR_SRC` and `SYNC_DIR_DST` variables.
- Uses `file(GLOB files ${SYNC_DIR_SRC}/*)` to enumerate entries.
- Uses `execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different ...)`.

## Control Flow
The script fails early if either required variable is missing. It globs all direct children in the source directory, extracts each basename, and copies each item to the destination path if different.

## State and Persistence Behavior
It writes/copies files under the destination directory. It is non-recursive as written and does not delete destination files that no longer exist in the source.

## Dependencies and Integration Points
`ctest_helpers.cmake` uses this script in `create_test_executable` for `ADDITIONAL_DIRECTORIES`, generating custom targets that keep test runtime directories synced into binary output directories.

## Risks and Test Signals
Missing variables are fatal. Because it uses a simple glob and `copy_if_different`, nested directories or deletions are not fully synchronized. Errors from `copy_if_different` surface through CMake process failure.
