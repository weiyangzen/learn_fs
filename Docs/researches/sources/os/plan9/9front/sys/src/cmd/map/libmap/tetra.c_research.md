# File Research: sources/os/plan9/9front/sys/src/cmd/map/libmap/tetra.c

Implements a conformal map of the Earth onto a tetrahedron. The file documents a multi-stage mapping: stereographic projection of tetrahedral faces, rational complex transform, and elliptic-integral mapping of sectors.

Key functions:
- `tetra()` initializes tetrahedral poles, face transformations, elliptic constants, complete integrals, translations, and rotations.
- `twhichp()` chooses the nearest and next-nearest tetrahedron face poles for an input place.
- `Xtetra()` normalizes to the selected face, stereographically projects, applies complex transforms and `elco2()`, rotates/translates into final tetrahedral layout.
- `tetracut()` supplies custom cut behavior for face boundaries and southern cuts.

This is one of the most complex map projection implementations and depends heavily on complex arithmetic, stereographic projection, normalization, and cut helpers.
