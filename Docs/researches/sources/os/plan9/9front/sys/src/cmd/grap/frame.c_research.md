# File Research: sources/os/plan9/9front/sys/src/cmd/grap/frame.c

Frame emission for `grap`. It tracks default frame height/width and optional custom side drawing attributes. `frame` writes pic code for `Frame` as a box at origin; if sides were specified, it emits an invisible frame and individual side lines, substituting customized side descriptors.

`frameht`, `framewid`, and `frameside` are parser actions. A side-less descriptor applies to all four sides by recursively setting top, bottom, left, and right.
