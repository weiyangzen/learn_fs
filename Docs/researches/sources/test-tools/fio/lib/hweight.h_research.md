# sources/test-tools/fio/lib/hweight.h

Purpose: declares portable Hamming weight functions.

Important APIs/functions: `hweight8`, `hweight32`, and `hweight64` declarations over fixed-width integer types.

Control flow/state: no state in the header; callers receive integer counts of set bits.

Dependencies/integration: includes `inttypes.h` and is used by portable bit-manipulation code.

Risks/test signals: compile-time type widths matter. Tests should compare results against known popcounts and, where available, compiler builtin popcounts.
