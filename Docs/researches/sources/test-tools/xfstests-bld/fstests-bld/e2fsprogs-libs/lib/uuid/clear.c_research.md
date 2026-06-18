# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/clear.c

## Purpose
`clear.c` implements `uuid_clear()`, the libuuid API for setting a UUID to the nil value.

## Important APIs, Types, and Functions
The public function is `uuid_clear(uuid_t uu)`.

## Control Flow
The function calls `memset(uu, 0, 16)`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the caller-provided UUID buffer. Dependencies are `string.h` and `uuidP.h`. Risks are minimal but include callers passing invalid buffers. Test signals are nil UUID comparisons and `uuid_is_null()` returning true after clearing.
