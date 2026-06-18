# File Research: sources/os/plan9/9front/sys/src/cmd/pic/print.c

`print.c` walks `objlist` and renders each object through the backend functions from `pltroff.c`. It handles troff passthrough, boxes, blocks, circles, ellipses, arcs, lines, arrows, splines, moves, text, invisible objects, arrowheads, fill, dash/dot styles, and attached text labels.

`dotline()` and `dotbox()` synthesize dotted or dashed geometry by subdividing lines. `dotext()` vertically stacks all text strings associated with an object.

Risk note: some expressions such as `move(ox + isright(m) ? x1 : -x1, oy)` rely on C precedence in a way that appears unintended; as written they test `(ox + isright(m))` rather than adding a signed radius to `ox`.
