# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/arcgen.c

Generates `pic` arc objects from parsed attributes. It computes start, end, center, radius, arrowhead sizing, clockwise handling, fill state, invisibility, and current-direction updates.

Default arcs use current position, direction, and `arcrad`; `TO` without `AT` derives a center from chord midpoint and radius, expanding radius if too small. Clockwise arcs swap start/end and arrowhead orientation for output compatibility.

The resulting object stores start, end, arrow dimensions, radius, head flags, clockwise flag, fill flags, and fill value. It also updates `curx/cury` to the logical arc endpoint.

`arc_extreme` computes bounding-box extremes by considering endpoints plus quadrant extrema on the circular arc.
