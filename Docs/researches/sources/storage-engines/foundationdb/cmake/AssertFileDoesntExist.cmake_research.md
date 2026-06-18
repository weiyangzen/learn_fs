# sources/storage-engines/foundationdb/cmake/AssertFileDoesntExist.cmake

## Purpose
Provides a configure-time guard that fails if a legacy generated file exists in the source tree.

## Important APIs, Types, and Functions
Uses the `FILE` variable supplied by the caller, builds a multi-line diagnostic in `error_msg`, joins it, and calls `message(FATAL_ERROR)` when the file exists.

## Control Flow and Integration
The caller includes or runs this script with `FILE` set. The script checks `EXISTS`, reports that a previous old `make` build likely left `versions.h`, and tells the user to clean the source directory.

## State and Persistence
Depends only on CMake built-ins `if(EXISTS)`, `list(JOIN)`, and `message`.

## Dependencies
No persistent state is written; it only observes source-tree filesystem state.

## Risks and Test Signals
Risk is limited to caller-provided `FILE`: an unset or wrong path weakens the guard or blocks an unrelated file. Test signal is a deliberate configure failure when the legacy artifact is present.
