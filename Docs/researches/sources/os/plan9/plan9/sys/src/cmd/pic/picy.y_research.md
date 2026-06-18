# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/picy.y

Yacc grammar for `pic`. It defines token numbers for object types, language keywords, attributes, positions, functions, operators, and statement terminators, then maps parsed constructs to generator and utility calls.

Top-level grammar recognizes picture statements inside `.PS/.PE`: primitives, blocks, named places, assignments, direction changes, print/reset, copy, for, if, and empty statements. Primitives dispatch to box/circle/ellipse/arc/line/arrow/spline/move/text/troff/block generators.

Attribute grammar translates dimensions, directions, from/to/at/by, with-corner/position, same, text attributes, heads, dot/dash/chop/fill/noedge, and nested text lists into the global attribute array.

Position grammar supports coordinates, relative offsets, position arithmetic, mixed x/y coordinates, interpolation, named places, object corners, first/last/nth references, and block member references.

Expression grammar implements arithmetic, comparisons, boolean operators, assignment, object component lookup, block variable lookup, math functions, random, min/max, and integer conversion.
