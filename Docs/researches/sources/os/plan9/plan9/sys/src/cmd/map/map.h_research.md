# File Research: sources/os/plan9/plan9/sys/src/cmd/map/map.h

Shared interface for the map command and libmap projections.

Defines:
- Constants: `PI`, `TWOPI`, `RAD`, earth eccentricity constants, `FUZZ`, `UNUSED`.
- Coordinate types:
  - `struct coord`: radians plus cached sine/cosine.
  - `struct place`: normalized latitude and west longitude.
- Projection type: `typedef int (*proj)(struct place *, double *, double *)`.
- `struct index`: projection registry entry with name, factory, parameter count, cut handler, pole flags, spheroid flag, and limb iterator.

Declares:
- Projection factories and low-level `X...` projection functions.
- Limb/cut functions.
- Complex arithmetic helpers.
- Orientation/coordinate helpers.
- Renderer callbacks exported by `map.c`.
- Global `projection`.

Notes:
- `#pragma lib` and `#pragma src` wire Plan 9 build tooling to `libmap.a`.
- Several comments mark projections “not in library,” indicating command-local or unavailable projections in the wider source tree.
