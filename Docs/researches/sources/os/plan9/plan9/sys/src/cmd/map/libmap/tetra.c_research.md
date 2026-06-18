# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/tetra.c

Implements a conformal map of the earth onto an unfolded tetrahedron.

Major pieces:
- Static tetrahedral pole definitions and per-face projection table `tproj`.
- `tetra()` initializes constants, elliptic-integral scale factors, tetrahedral pole coordinates, and per-face orientation/twist rotations.
- `twhichp()` chooses the nearest and second-nearest tetrahedral poles for a point.
- `Xtetra()` normalizes a point into the selected face, stereographically projects, applies complex rational transforms and elliptic integral `elco2`, then rotates/translates into the unfolded tetrahedron.
- `tetracut()` handles seam crossing behavior for map line drawing.

Dependencies:
- Heavy use of libmap complex helpers, `Xstereographic`, `latlon`, `deg2rad`, and `norm`.
- `map.c` contains special grid handling for `projection == Xtetra`.

Behavior notes:
- Uses old K&R style `register i`.
- Mutates static `tx` and `ty` scale offsets during initialization, so repeated `tetra()` initialization would compound offsets if called more than once in the same process.
