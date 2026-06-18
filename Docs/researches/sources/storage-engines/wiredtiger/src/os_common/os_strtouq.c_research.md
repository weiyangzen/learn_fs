# sources/storage-engines/wiredtiger/src/os_common/os_strtouq.c

## Purpose
Provides a small unsigned 64-bit string conversion wrapper.

## Important APIs, Types, and Functions
`__wt_strtouq` returns `uint64_t` and accepts `const char *nptr`, `char **endptr`, and a numeric base.

## Control Flow
The function directly calls `strtoull` and casts the result to `uint64_t`.

## State and Persistence Behavior
No state is stored. The caller observes libc conversion behavior through the return value, `endptr`, and `errno`.

## Dependencies and Integration Points
This wrapper provides a portable WiredTiger-named conversion API used by configuration/tool parsing code that wants an unsigned 64-bit value.

## Risks and Edge Cases
Overflow and invalid input behavior are inherited from `strtoull`; the wrapper does not clear or inspect `errno`. On platforms where `unsigned long long` is wider or narrower than expected, the cast semantics matter, though WiredTiger assumes it can represent 64-bit values.

## Test Signals
Parse decimal, hex, octal/base-specific values, invalid input with `endptr`, max `uint64_t`, overflow with `errno`, and empty strings.
