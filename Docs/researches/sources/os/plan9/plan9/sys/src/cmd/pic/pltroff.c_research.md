# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/pltroff.c

Troff output backend for `pic`. It converts picture coordinates into troff motions and `\D` drawing commands, manages `.PS/.PE` wrapping, scaling, current output position, and line directives.

`openpl` bounds and possibly shrinks the picture to `maxpswid`/`maxpsht`, initializes coordinate transforms, emits diagnostic bounding comments, disables fill mode, and starts `.PS`. `closepl` restores position and fill state.

Primitive emitters draw lines, arrows, boxes, circles, ellipses, arcs, splines, dots, labels, and raw troff text. Text positioning uses troff width calculations and vertical half-line adjustments.

Fill support emits PostScript-specific `\X` BeginObject/EndObject commands compatible with dpost conventions, combining fill and optional stroke.
