# Research: sources/storage-engines/sqlite/ext/misc/windirent.h

## Purpose

`windirent.h` is a Windows/MSVC-only compatibility header that provides static `opendir()`, `readdir()`, and `closedir()` implementations using Win32 `_wfindfirst`, `_wfindnext`, and `_findclose`. On non-Windows or non-MSVC builds it is a no-op.

The shim allows SQLite extension code that expects POSIX-like directory iteration to compile on Windows while using UTF-8 directory names externally.

## Important APIs, Types, And Functions

- The header is enabled only when `_WIN32`, `_MSC_VER`, and not `SQLITE_WINDIRENT_H` are defined.
- It defines missing POSIX-like macros `S_ISREG`, `S_ISDIR`, `S_ISLNK`, a `mode_t` typedef, and a compact `struct dirent` with `d_ino`, `d_attributes`, and `d_name`.
- `DIR` stores a Win32 find handle and current `dirent`.
- `WindowsFileToIgnore()` filters hidden and system files.
- `opendir(const char *zDirName)` converts a UTF-8 path to UTF-16, appends `\*`, opens `_wfindfirst`, skips hidden/system entries, and returns a heap-allocated `DIR`.
- `readdir(DIR *pDir)` returns the cached first entry on first call, then loops `_wfindnext` skipping hidden/system entries and converting names back to UTF-8.
- `closedir(DIR *pDir)` closes the find handle when valid and frees the `DIR`.

## Control Flow

`opendir` allocates and clears a `DIR`, converts the supplied UTF-8 directory path to a wide string, appends a wildcard, copies it into `_wfinddata_t.name`, and starts iteration. It skips ignored entries immediately so the first `readdir` returns the first visible entry. `readdir` uses `d_ino` as a first-read sentinel/counter: the first call returns the cached entry and later calls fetch from the Win32 iterator.

## State And Persistence Behavior

State is entirely per-`DIR` and process-local. No directory contents are persisted. Returned `struct dirent *` points into the `DIR` and remains valid only until the next `readdir` or `closedir`.

## Dependencies And Integration Points

The header depends on Windows headers, MSVC/CRT `_wfinddata_t`, `_wfindfirst`, `_wfindnext`, `_findclose`, UTF conversion APIs, and SQLite memory allocation (`sqlite3_malloc64`, `sqlite3_free`). It is meant to be included inside C modules that already include SQLite definitions.

## Risks And Edge Cases

- Hidden and system files are silently skipped, which differs from POSIX `readdir`.
- `MultiByteToWideChar` is called with `sz` as both input length and output capacity after allocating `sz+3`; non-ASCII expansion is safe for UTF-16 code units in normal cases but conversion failure is not checked.
- Paths longer than `_wfinddata_t.name` capacity fail.
- `closedir(NULL)` returns `EINVAL` directly rather than `-1` with `errno`.
- `d_ino` is synthetic and used as an internal counter; applications cannot rely on inode semantics.
- The implementation uses backslash wildcard appending and may not handle paths already ending in a slash uniformly.

## Test Signals

Windows/MSVC tests should include UTF-8 directory names, first-entry caching, hidden/system file filtering, end-of-directory handling, long-path rejection, repeated open/close, and compatibility with code expecting only `d_name`. Non-Windows builds should verify including the header does not define symbols or change behavior.
