# File Research: sources/os/plan9/9front/sys/src/cmd/pic/arcgen.c

## Role

Generates `pic` arc objects and computes their bounding boxes.

## Main Behavior

`arcgen` interprets attributes for text, arrow heads, invisibility, arrow dimensions, radius/diameter, clockwise mode, from/to/at positions, direction, and fill. It computes default arc center/end based on current direction and radius, or derives a center from explicit endpoints and radius.

Clockwise arcs swap start/end roles and adjust arrow-head placement. The generated object records start, end, radius, arrow dimensions, fill, and flags.

## Bounding Box

`arc_extreme` computes extrema for a circular arc by considering start/end points and quadrant boundary points that lie on the swept arc. `quadrant` classifies vectors around the center.

## State Updates

The global current point is advanced to the arc endpoint according to direction and clockwise handling. `extreme` is called with computed bounds.
