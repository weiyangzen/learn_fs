<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.h

## Purpose
This small public header declares the charset-detection API implemented by `localcharset.c`.

## Important APIs, Types, and Functions
It declares `extern const char * locale_charset(void);` inside an `extern "C"` block for C++ compatibility and uses include guards.

## Control Flow
No runtime flow; it is a declaration-only header.

## State and Persistence
No state is stored here. The returned pointer contract says callers must not free it because it is statically allocated or cached by the implementation.

## Dependencies and Integration Points
Included by `localcharset.c` and any code needing the current locale's canonical encoding. In this tree, catalog conversion setup uses it indirectly through `loadmsgcat.c`.

## Risks
Callers might incorrectly free or mutate the returned string. The API returns a non-canonical name when canonicalization fails, so users must tolerate unknown encodings.

## Test Signals
Compile C and C++ consumers and verify they can call `locale_charset()` and treat the result as read-only.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/localcharset.h -->
