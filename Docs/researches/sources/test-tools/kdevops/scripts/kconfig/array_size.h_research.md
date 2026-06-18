# sources/test-tools/kdevops/scripts/kconfig/array_size.h

## Purpose
This header provides the standard `ARRAY_SIZE(arr)` macro for compile-time-ish array element counting.

## Important APIs, Types, And Functions
`ARRAY_SIZE(arr)` expands to `sizeof(arr) / sizeof((arr)[0])`.

## Control Flow
There is no runtime control flow; the macro is evaluated by the C compiler wherever used.

## State And Persistence
It has no state and no side effects.

## Dependencies And Integration Points
`hashtable.h` uses this macro for `HASH_SIZE(name)`. Any C file including the Kconfig utility headers can depend on it.

## Risks And Test Signals
The macro does not protect against pointer arguments, so passing a pointer returns a bogus size ratio. Compile tests should include a real array user such as `HASHTABLE_DEFINE` and avoid pointer misuse.
