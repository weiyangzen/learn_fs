# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/com64.c

Common 64-bit integer emulation rewrite support for Plan 9 compilers targeting machines without direct `vlong` support. It creates AST nodes for runtime helper functions such as `_addv`, `_divv`, `_eqv`, `_f2v`, `_v2d`, `_vasop`, and increment/decrement helpers.

`com64init` initializes all helper nodes and an encoded-type conversion table. `com64` rewrites vlong arithmetic, comparisons, casts, logical tests, compound assignments, and inc/dec operations into helper function calls when `machcap` does not handle them natively.

`bool64` converts vlong truth tests to `_testv`. The file also includes common float/integer conversion helpers and `convvtox`, which masks/sign-extends constants to a target integer type width.
