# sources/user-network-fs/nfs-utils/support/misc/file.c

## Purpose
Implements generic state pathname construction and base-directory validation shared by nfs-utils state-file users.

## Important APIs, Types, and Functions
`generic_make_pathname()` and `generic_setup_basedir()`.

## Control Flow
Path construction joins base and leaf with one slash after checking `PATH_MAX` and `snprintf()` bounds. Base setup validates length, `lstat()` existence, dirname usability, logs the selected directory, and copies it into the caller buffer.

## State and Persistence Behavior
Returned pathnames are heap-owned by callers. Base directory buffers are caller-owned process configuration; underlying directories are persistent filesystem state.

## Dependencies and Integration Points
Used by `xtab.c` and NSM/statd path setup helpers. Depends on `misc.h`, `xlog`, libc path/stat functions.

## Risks and Edge Cases
`generic_setup_basedir()` assumes `parentdir` is non-NULL. It checks existence but not directory type or permissions. Error messages omit trailing newlines in some cases.

## Test Signals
Test long paths, NULL/empty handling by callers, nonexistent paths, relative `.` dirname rejection, normal state directory setup, and allocation failure.
