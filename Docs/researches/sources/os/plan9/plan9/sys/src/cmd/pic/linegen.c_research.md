# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/linegen.c

Generates line, arrow, and spline objects. It accumulates one or more relative segments from direction, `TO`, `BY`, `THEN`, `FROM`, and `AT` attributes, with default line width/height from variables.

Attributes control heads, invisibility, no-edge, dotted/dashed style, same-as-previous segment, arrowhead dimensions, chop distances, fill, and text. `CHOP` shortens the first and last segments along their direction, defaulting to circle radius when no explicit distance is supplied.

The created object stores final endpoint, arrowhead dimensions, segment count, and all segment deltas. It updates extremes differently for straight lines/arrows and splines, approximating spline extents from neighboring control points.

Current position is advanced to the final endpoint, and previous delta state is saved for `same`.
