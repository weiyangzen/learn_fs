# File Research: sources/os/plan9/9front/sys/src/cmd/plot/libplot/vec.c

`vec.c` draws a clipped vector from the current pen position to a new point. It converts both endpoints, rejects huge coordinates, updates the current pen position, performs Cohen-Sutherland-style clipping, and delegates to `m_vector()`.
