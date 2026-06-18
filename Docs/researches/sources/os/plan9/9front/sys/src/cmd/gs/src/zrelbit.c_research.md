# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zrelbit.c

## Purpose
Implements relational, boolean, and bitwise PostScript operators.

## Key Functions
- `zeq()`, `zne()`, `zge()`, `zgt()`, `zle()`, and `zlt()` implement equality and ordering.
- `zmax()` and `zmin()` implement nonstandard extrema operators.
- `zand()`, `znot()`, `zor()`, `zxor()`, and `zbitshift()` implement boolean/integer bit operations.
- `zidenteq()` and `zidentne()` test object identity.
- `obj_le()` compares numeric or string operands.

## Important Behavior
- String comparisons require read access.
- Ordering supports numbers and strings only.
- Boolean operators require both operands to be boolean; integer operators require both operands to be integer.
- Oversized bit shifts yield zero.
- Several functions are public so FunctionType 4 calculator support can reuse them.

## Research Notes
Core scalar operator implementation used both directly by PostScript and internally by calculator functions.
