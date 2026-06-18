# sources/sync-backup/casync/src/dirent-util.h

## Purpose

`dirent-util.h` declares directory-entry helper functions and a macro for safe directory iteration with errno handling.

## Important APIs, Types, and Functions

It declares `dirent_is_file_with_suffix()` as `_pure_` and `readdir_no_dot()`. `FOREACH_DIRENT_ALL(de, d, on_error)` expands to a loop that clears `errno` before each `readdir()`, runs `on_error` when EOF is accompanied by an errno, and otherwise exposes every returned entry.

## Control Flow

The macro provides structured iteration where caller-supplied `on_error` can return, break, or otherwise handle the directory error. `readdir_no_dot()` gives a function form for skipping dot entries.

## State and Persistence Behavior

The API advances caller-owned `DIR *` streams and stores no state.

## Dependencies and Integration Points

It includes `<dirent.h>`, `<errno.h>`, `<stdbool.h>`, and `util.h`. Files scanning stores or filesystem trees can use these helpers for consistent dot-entry handling.

## Risks and Edge Cases

Macros with embedded control flow can be misused if `on_error` has side effects or declarations that do not fit the expansion context. The header uses `#pragma once` unlike some local headers that use include guards; this is acceptable for supported compilers.

## Test Signals

Tests should compile macro users in different statement contexts and validate errno behavior on mocked `readdir()` failure.
