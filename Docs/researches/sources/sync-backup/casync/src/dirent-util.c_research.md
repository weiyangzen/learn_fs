# sources/sync-backup/casync/src/dirent-util.c

## Purpose

`dirent-util.c` provides directory-entry helpers derived from systemd utilities. It filters regular/link/unknown non-hidden entries by suffix and wraps `readdir()` to skip `.` and `..`.

## Important APIs, Types, and Functions

`dirent_is_file_with_suffix()` accepts `DT_REG`, `DT_LNK`, and `DT_UNKNOWN`, rejects names beginning with `.`, accepts any suffix when suffix is `NULL`, and otherwise tests `endswith(de->d_name, suffix)`. `readdir_no_dot()` loops over `readdir()` until it sees an entry that is not `.` or `..` or reaches EOF/error.

## Control Flow

Both functions are simple filters around libc `readdir()` and `struct dirent`. `readdir_no_dot()` preserves libc error signaling through `errno` exactly as `readdir()` does; callers need to clear/check errno if they need to distinguish EOF from error.

## State and Persistence Behavior

No persistent state is stored. `readdir_no_dot()` advances the directory stream.

## Dependencies and Integration Points

It includes `dirent-util.h` and uses `IN_SET`, `endswith`, and `dot_or_dot_dot()` from `util.h`. Store/index directory scanners and GC are likely consumers.

## Risks and Edge Cases

Rejecting all dot-prefixed names may be correct for chunk files but is not a generic file predicate. Accepting `DT_UNKNOWN` means callers may need `stat()` later. Suffix matching does not require the suffix to be a true extension boundary.

## Test Signals

Tests should cover visible/hidden files, symlinks, directories, unknown d_type if mockable, null suffix, positive/negative suffixes, and `readdir_no_dot()` behavior on empty directories and errors.
