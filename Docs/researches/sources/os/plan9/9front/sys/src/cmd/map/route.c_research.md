# File Research: sources/os/plan9/9front/sys/src/cmd/map/route.c

Implements `route`, a helper that computes a `map -o` orientation placing two latitude/longitude points on the equator of a standard projection, optionally emitting a great-circle track.

Key behavior:
- Parses `route [-t] [-i] lat lon lat lon`.
- Uses `orient`, `normalize`, and `invert` to rotate coordinate systems and solve for a pole/twist placing endpoints symmetrically.
- Without `-t`, prints a suggested `-o ... -w ...` argument line.
- With `-t`, emits interpolated coordinates along the great-circle route and terminates with `"`, suitable for `map -t`.
- `-i` flips the orientation by using `dir = +90` instead of the default `-90`.

Important dependencies: `map.h`, `orient`, `deg2rad`, `normalize`, `invert`, and `lat/lon` rotation helpers.

Notable risks:
- Uses degrees at the command interface but internal radians in `struct place`; helper conversion is essential.
- The margin/window suggestion is heuristic and based on transformed longitude separation.
