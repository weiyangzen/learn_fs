# File Research: sources/os/plan9/plan9/sys/src/cmd/map/libmap/hex.c

Read fully: 122 lines, 2283 bytes. SHA-256 prefix: `fd39dd8f49d25d13`.

Implements a hexagonal world projection with special cut handling. `hex()` initializes cut longitudes, elliptic constants, reference geometry, reflection centers, and returns `Xhex`. `Xhex()` handles northern/southern symmetry, equator/cut singularities, normalizes to a hemisphere, stereographically projects, applies complex algebra including cube root and square root, runs `elco2()`, and reflects southern points across hex edges. `hexcut()` tests whether an edge crossing is acceptable against three cut longitudes.

Dependencies: `reduce`, `ckcut`, `latlon`, `norm`, `Xstereographic`, `cdiv`, `csq`, `ccubrt`, `csqrt`, `elco2`.

Risk notes: requires real map cut helpers. Many static constants are initialized by calling the projection during setup; reentrancy is not supported.
