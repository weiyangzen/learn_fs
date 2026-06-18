# sources/storage-engines/wiredtiger/src/include/bitstring.h

## Purpose
This small public-domain-derived header defines the byte and mask layout macros for compact bitstrings. WiredTiger keeps these preprocessor macros separate from inline functions so layout calculations can be reused without pulling in the full helper implementation.

## Important APIs, Types, And Functions
`__bit_byte(bit)` maps a bit index to its containing byte by shifting right three bits. `__bit_mask(bit)` creates the mask for the bit within that byte using the low three bits. `__bitstr_size(nbits)` returns the number of bytes needed to store `nbits`, rounded up to the next byte.

## Control Flow
There is no runtime control flow in this file. All three definitions are arithmetic macros expanded at call sites. The inline header builds allocation, set, clear, range, and first-bit search operations on top of these definitions.

## State And Persistence Behavior
The file defines the memory layout contract for bitstrings: bits are packed little-bit-endian within each byte, with bit zero in mask `1 << 0`. It does not allocate or mutate memory itself. Any persistent behavior is indirect when other components use bitstrings for tracking on-disk or verification state.

## Dependencies And Integration Points
The companion file `bitstring_inline.h` depends on these macros. Other low-level structures can use `__bitstr_size` to size allocations without duplicating rounding logic. The block manager verification code is one likely consumer because it uses byte arrays to track file/checkpoint fragments.

## Risks
The macros do not validate bounds, integer width, or side effects. Passing expressions with side effects can evaluate more than once in some use contexts outside this file. Changing bit order or size rounding would silently corrupt all users that share bitstring memory with existing assumptions.

## Test Signals
Test byte sizing at zero, one, seven, eight, and boundary values; bit set/test/clear behavior through the inline helpers; range operations across one and multiple bytes; and any consumer that serializes or reports bitstring-backed state.
