# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/isnull.c

## Purpose
`isnull.c` implements the nil UUID predicate.

## Important APIs, Types, and Functions
The public function is `uuid_is_null(const uuid_t uu)`.

## Control Flow
The function scans all 16 bytes and returns `0` on the first nonzero byte or `1` if all bytes are zero.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no persistent state. Dependencies are `uuidP.h`. Risks are minimal, limited to invalid caller buffers. Test signals are `uuid_clear()` followed by true, and generated UUIDs returning false.
