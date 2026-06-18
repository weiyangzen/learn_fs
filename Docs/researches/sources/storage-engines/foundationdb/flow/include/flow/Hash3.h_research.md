# sources/storage-engines/foundationdb/flow/include/flow/Hash3.h

## Purpose
`Hash3.h` declares C-linkage prototypes for Bob Jenkins lookup3 hash functions used by Flow utilities.

## Important APIs, Types, And Functions
It exposes `hashlittle(const void*, size_t, uint32_t)` and `hashlittle2(const void*, size_t, uint32_t*, uint32_t*)`.

## Control Flow
The header has no implementation; callers pass a byte buffer, length, and seed values. `hashlittle2` updates two hash outputs in place.

## State And Persistence Behavior
There is no retained state. Hash outputs may be persisted by callers, so implementation compatibility matters.

## Dependencies And Integration Points
It depends on standard integer and size types and links to `Hash3.c`. `FastAlloc` instrumentation includes this header for backtrace/sample hashing.

## Risks And Edge Cases
Callers must pass valid memory for the specified length and non-null output pointers for `hashlittle2`. Changing implementation would alter hashes used in diagnostics or metadata.

## Test Signals
Known-vector tests, empty-buffer behavior, seed variation, C/C++ linkage tests, and sanitizer checks for buffer bounds are useful.
