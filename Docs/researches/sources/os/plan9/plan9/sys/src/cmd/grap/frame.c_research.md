# File Research: sources/os/plan9/plan9/sys/src/cmd/grap/frame.c

This file emits the `pic` frame around a graph. It stores default frame height/width and optional side-specific line descriptions.

`frame` writes `frameht`, `framewid`, and a `Frame` box. With no custom sides it emits a normal visible box; with custom sides it emits an invisible frame and explicit lines for top, bottom, left, and right, substituting remembered side descriptors.

`frameside` maps side tokens to side strings and can apply a line descriptor to all sides when no side is specified.
