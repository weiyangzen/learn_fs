# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/blockgen.c

Handles grouped `pic` constructs: braces `{...}` and bracketed blocks `[...]`.

`leftthing` saves current position/direction and, for `[...]`, starts a `BLOCK` object while resetting local bounds. `rightthing` restores state and emits either a `MOVE` for braces or a `BLOCKEND` object paired with the block start.

`blockgen` computes the final block size and placement from enclosed-object bounds plus attributes like height, width, with-corner, at/from, invis, and text. It updates global extremes and cursor position according to direction.

`blockadj` shifts every enclosed object by the final block translation and adjusts embedded absolute coordinates for lines, splines, arrows, and arcs.
