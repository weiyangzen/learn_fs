# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/genhash

Shell generator for terminfo capability ID tables and perfect-hash lookup functions.

Key responsibilities:
- Reads `term.h`.
- Extracts enum members from:
  - `enum TIFLAGS`
  - `enum TINUMS`
  - `enum TISTRS`
- Generates:
  - static ID string arrays,
  - `_ti_flagid`, `_ti_numid`, `_ti_strid`,
  - `_ti_flagindex`, `_ti_numindex`, `_ti_strindex`,
  - perfect hash functions via `nbperf`.

Inputs/tools:
- `term.h`
- `awk`
- `sed`
- `nbperf`

Role in subsystem:
- Keeps runtime capability lookup tables derived directly from the public capability enum definitions.
