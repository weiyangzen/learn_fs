<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/hash-string.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/hash-string.h

## Purpose
This header implements GNU gettext's string hash function for `.mo` hash-table lookup.

## Important APIs, Types, and Functions
The single key function is `hash_string(const char *str_param)`, a static inline implementation of the PJW hash over unsigned bytes with `HASHWORDBITS` fixed to 32.

## Control Flow
The function initializes `hval` to zero, shifts it four bits per byte, adds the byte, extracts high bits into `g`, and folds those bits back into the hash. It stops at NUL and returns an unsigned long hash value.

## State and Persistence
There is no state. The returned hash is used transiently to probe `.mo` hash tables and build augmented sysdep hash tables.

## Dependencies and Integration Points
Used by `dcigettext.c` for message lookup and `loadmsgcat.c` while constructing in-memory hash entries for system-dependent strings.

## Risks
Correctness must match the hash used by GNU `.mo` generation tools. Changing it breaks catalog lookups. It assumes `unsigned long int` has at least 32 bits.

## Test Signals
Compare hash values for known strings against GNU gettext fixtures and verify hash-table lookup finds translations in catalogs with hash sections.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/hash-string.h -->
