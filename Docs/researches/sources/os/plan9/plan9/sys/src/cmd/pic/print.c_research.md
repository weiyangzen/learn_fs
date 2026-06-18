# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/print.c

Walks the `pic` object list and emits drawing operations through the troff backend. It handles each object type, applies visibility/fill/style bits, places text, emits arrowheads, and updates output position.

Boxes/blocks compute bounds from center and dimensions; blocks themselves are not drawn but may carry text. Circles, ellipses, arcs, lines, arrows, splines, moves, text, and raw troff each dispatch to backend primitives.

Dotted and dashed lines/boxes are synthesized by subdividing line segments into dots or dash/space intervals. Splines are passed to the backend with dash metadata, though backend dash handling is limited.

`dotext` vertically spaces all text strings attached to an object, calling `label` with half-line offsets.
