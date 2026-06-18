# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.h

Header declaring Vorbis backend registry bounds and arrays.

Important contents:
- Defines backend-count constants:
  - `VI_TRANSFORMB 1`
  - `VI_WINDOWB 1`
  - `VI_TIMEB 1`
  - `VI_FLOORB 2`
  - `VI_RESB 3`
  - `VI_MAPB 1`
- Declares `_floor_P`, `_residue_P`, and `_mapping_P`.

Integration points:
- Included by setup/header code and backend dispatch users.
- Constants are used to validate backend type numbers during Vorbis setup-header parsing.

Risk and review signals:
- Constants must match actual arrays in `registry.c`.
- Any new backend requires coordinated changes in validation and implementation.

Filesystem relevance:
- No filesystem logic. It is codec backend registry metadata.
