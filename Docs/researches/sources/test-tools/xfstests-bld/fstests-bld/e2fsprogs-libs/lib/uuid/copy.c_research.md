# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/copy.c

## Purpose
`copy.c` implements `uuid_copy()`, copying one UUID byte array to another.

## Important APIs, Types, and Functions
The public function is `uuid_copy(uuid_t dst, const uuid_t src)`.

## Control Flow
The function calls `memcpy(dst, src, 16)`.

## State, Persistence, Dependencies, Risks, and Test Signals
State is the caller-provided source and destination buffers. Dependencies are `string.h` and `uuidP.h`. Risks are minimal, with standard `memcpy` overlap caveats. Test signals are identical parsed/unparsed UUIDs after copy and compare returning zero.
