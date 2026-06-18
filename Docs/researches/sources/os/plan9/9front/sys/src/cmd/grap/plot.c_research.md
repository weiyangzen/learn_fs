# File Research: sources/os/plan9/9front/sys/src/cmd/grap/plot.c

Plot primitive output for `grap`. It emits pic lines/arrows, circles or default bullet markers, raw pic text, string plots, formatted numeric plots, and connected `next` paths. `xyname` converts a `Point` to an `xy_<coord>` macro call, applying log transforms with validation.

`numlist` implements the default numeric input behavior: one number becomes auto-incremented x plus y; multiple numbers plot at the first x. Named draw descriptors store line/marker attributes on coordinate objects for later path drawing.
