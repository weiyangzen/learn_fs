# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/compare.c

## Purpose
`compare.c` implements lexicographic UUID comparison.

## Important APIs, Types, and Functions
The public function is `uuid_compare(const uuid_t uu1, const uuid_t uu2)`. The `UUCMP` macro compares corresponding fields after unpacking.

## Control Flow
The function unpacks both UUID byte arrays into `struct uuid` fields and compares time_low, time_mid, time_hi, clock_seq, and node bytes in order, returning -1, 0, or 1.

## State, Persistence, Dependencies, Risks, and Test Signals
No persistent state is used. Dependencies include `uuidP.h` and `uuid_unpack()`. Risks are mainly semantic: ordering is field-based UUID order, not raw memcmp byte order. Test signals are equality returning zero and stable ordering for known UUID pairs.
