# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/polyconic.c

Implements polyconic projection.

Key behavior:
- `polyconic()` returns `Xpolyconic`.
- For non-equatorial latitudes, computes `r = cos/sin`, `alpha = lon*sin(lat)`, then applies standard polyconic formulas.
- For near-equatorial latitudes, uses a series approximation to avoid singular division by small `sin(lat)`.
- Always returns `1`.

Dependencies:
- Uses `struct place` cached trigonometric fields from `zcoord.c`.
