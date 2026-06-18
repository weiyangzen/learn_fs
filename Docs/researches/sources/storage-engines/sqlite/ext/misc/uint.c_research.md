# sources/storage-engines/sqlite/ext/misc/uint.c

## Purpose
Registers the `uint` collation, which compares text lexicographically except that embedded digit runs compare by unsigned numeric magnitude.

## Important APIs, Types, And Functions
`uintCollFunc()` implements the collation. `sqlite3_uint_init()` registers it with `sqlite3_create_collation()`.

## Control Flow
The comparator walks both byte strings. When both current bytes are digits, it skips leading zeros, compares digit-run length to determine magnitude, then falls back to `memcmp()` for equal-length runs. Non-digit bytes compare by ordinary byte difference, and exhausted input compares by remaining length.

## State And Persistence Behavior
The collation keeps no state and writes no data. Persistent impact occurs when schemas or indexes use `COLLATE uint`; index ordering then depends on this comparator.

## Dependencies And Integration Points
Depends on SQLite collation registration and C `isdigit()`/`memcmp()`. It integrates with ORDER BY, comparisons, and indexes that select this collation.

## Risks And Edge Cases
Only ASCII digit bytes are numeric. Signs, decimal points, and exponent notation are treated as normal text. Leading zeros do not affect numeric magnitude, so distinct strings may compare equal across a numeric run until later bytes differ. Passing signed non-ASCII bytes to `isdigit()` can be locale/undefined-behavior sensitive because the code does not cast to unsigned char.

## Test Signals
Tests should compare natural-sort examples, leading-zero equivalence, arbitrary-length digit runs beyond 64 bits, mixed text and digits, signs/decimals, empty strings, and indexed ORDER BY behavior.
