# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/twocirc.c

Provides common two-circle geometry for projections whose meridians and parallels are circular arcs.

Key pieces:
- `quadratic()` solves a quadratic branch used by circle intersection.
- `twocircles()` computes intersection of a meridian circle and parallel circle, handling symmetry and near-axis cases.
- `globular()`/`Xglobular()` implement globular projection using normalized longitude/latitude and circle intersections.
- `vandergrinten()`/`Xvandergrinten()` implement Van der Grinten projection with transformed latitude parameter and the same circle-intersection helper.

This file supplies two registered projections from one shared geometric primitive.
