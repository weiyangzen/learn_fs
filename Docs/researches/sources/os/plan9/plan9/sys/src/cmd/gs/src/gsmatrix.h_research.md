# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmatrix.h

Defines `gs_matrix` as six floats: `xx`, `xy`, `yx`, `yy`, `tx`, `ty`, matching PostScript transformation matrix semantics. Provides constant-initializer macros, identity body, and fast-path predicates `is_xxyy` and `is_xyyx`.

Declares matrix construction, arithmetic, point/distance/bbox transforms, and stream serialization functions. It forward-declares `stream` so callers do not need full stream internals for prototypes.
