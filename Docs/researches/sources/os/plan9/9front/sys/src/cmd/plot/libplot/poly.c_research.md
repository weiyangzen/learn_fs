# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/poly.c

`poly.c` draws one or more polylines from packed vertex arrays. Each polygon/list begins with a vertex count, then a pointer to interleaved x/y doubles. It moves to the first point and vectors through remaining points.
