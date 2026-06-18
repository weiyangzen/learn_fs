# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/frame.c

`frame.c` changes the active plotting frame relative to the base environment `e0`. It updates origin, side lengths, scale factors, and the curve approximation quantum for `e1`.

The function supports nested or adjusted coordinate windows while preserving the current environment structure.
