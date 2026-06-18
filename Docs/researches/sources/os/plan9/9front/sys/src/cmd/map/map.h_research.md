# File Research: sources/os/plan9/9front/sys/src/cmd/map/map.h

Defines the shared map projection API and common geographic data structures used by `map`, `route`, symbol rendering, and the projection library.

Key behavior:
- Defines radians/constants, earth eccentricity constants, and `coord`/`place` structures with angle plus cached sine/cosine.
- Defines `proj` as a projection callback taking a `place` and returning projected x/y.
- Defines `struct index`, the projection registry entry with name, constructor, parameter count, cut handler, pole behavior, spheroid flag, and limb iterator.
- Declares projection constructors, special projection functions, cut handlers, complex math helpers, orientation/normalization helpers, symbol helpers, plotting helpers, and the global `projection`.

Important dependencies: Plan 9 map projection library archive via `#pragma lib`/`#pragma src`.

Notable risks:
- Projection functions use integer return conventions shared across many files; callers depend on `-1/0/1` meanings.
- Many declarations are old-style Plan 9 C interfaces with global state coupling.
