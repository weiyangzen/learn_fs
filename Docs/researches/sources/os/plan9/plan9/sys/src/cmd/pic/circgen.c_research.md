# File Research: sources/os/plan9/plan9/sys/src/cmd/pic/circgen.c

Generates circle and ellipse objects. It reads defaults from `circlerad`, `ellipsewid`, and `ellipseht`, then applies radius, diameter, width, height, same, with-corner, at, invis, no-edge, dot/dash, fill, and text attributes.

Circle radius is forced equal on both axes; ellipses store separate horizontal/vertical radii. Invalid non-positive radii produce warnings.

Placement follows current direction unless `AT` is used. The object updates extremes using the full bounding rectangle and advances current position to the appropriate edge.
