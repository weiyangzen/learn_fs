# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/blkid/version.c

## Purpose
`version.c` returns the libblkid library version and release date derived from the e2fsprogs version header.

## Important APIs, Types, and Functions
The public functions are `blkid_parse_version_string()` and `blkid_get_library_version()`. Static state is `lib_version` and `lib_date`.

## Control Flow
`blkid_parse_version_string()` walks a version string, ignores dots, accumulates decimal digits, and stops at the first non-digit/non-dot. `blkid_get_library_version()` optionally returns string pointers and returns the parsed integer.

## State, Persistence, Dependencies, Risks, and Test Signals
State is compile-time constant. Dependencies are `<blkid/blkid.h>` and `../../version.h`. Risks include ambiguous numeric encoding for versions with more components or suffixes. Test signals are expected parsed values for `E2FSPROGS_VERSION` and non-NULL returned date/version strings.
