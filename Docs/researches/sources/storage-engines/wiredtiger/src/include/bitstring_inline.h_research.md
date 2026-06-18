# sources/storage-engines/wiredtiger/src/include/bitstring_inline.h

## Purpose
This header implements inline bitstring allocation and manipulation helpers using the layout macros from `bitstring.h`. It provides fast, dependency-light primitives for compact boolean arrays inside the storage engine.

## Important APIs, Types, And Functions
`__bit_alloc` allocates a zeroed byte array large enough for `nbits`. `__bit_test`, `__bit_set`, and `__bit_clear` operate on one bit. `__bit_nclr` and `__bit_nset` clear or set inclusive ranges. `__bit_ffc` finds the first clear bit, and `__bit_ffs` finds the first set bit, returning `0` on success and `-1` when no matching bit exists.

## Control Flow
Single-bit helpers compute byte and mask and update the target byte directly. Range helpers compute start and stop bytes; if the range is within one byte they combine masks, otherwise they update the partial start byte, full middle bytes, and partial stop byte. First-bit search helpers scan bytes from zero to `__bit_byte(nbits - 1)` and then scan the low bits of the first byte that is not all-set or not all-clear, rejecting matches beyond `nbits` in the final partial byte.

## State And Persistence Behavior
The helpers mutate caller-owned `uint8_t` buffers. `__bit_alloc` uses WiredTiger allocation through `__wt_calloc`, so memory is session-accounted and zero-initialized. There is no locking or atomicity; concurrent users must synchronize externally. The bit layout is stable because it is inherited from `bitstring.h`.

## Dependencies And Integration Points
The implementation depends on `WT_SESSION_IMPL`, `WT_INLINE`, `__wt_calloc`, and the `__bit_*` macros. It is suitable for hot paths because functions are inlined and avoid function pointer dispatch. Consumers include low-level tracking arrays such as block verification fragment maps and any component that needs dense bit sets.

## Risks
The API assumes valid buffers and valid inclusive ranges. Passing `start > stop`, out-of-range bit indexes, or a buffer shorter than `__bitstr_size(nbits)` causes memory corruption. `__bit_nclr` and `__bit_nset` rely on 8-bit masks; changes to `uint8_t` assumptions or signed promotion could affect unusual platforms. Search is linear in bytes, so very large bitstrings can become expensive.

## Test Signals
Cover zero-length searches, first and last bits in partial bytes, all-set and all-clear buffers, single-byte and multi-byte range set/clear, alternating patterns, allocation size, and sanitizer/diagnostic tests for callers' boundary calculations.
