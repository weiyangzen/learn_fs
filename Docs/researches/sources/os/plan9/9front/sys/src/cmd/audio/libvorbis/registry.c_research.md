# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libvorbis/registry.c

Backend registry implementation for Vorbis floor, residue, and mapping backends.

Important contents:
- Declares external backend bundles: `floor0_exportbundle`, `floor1_exportbundle`, `residue0_exportbundle`, `residue1_exportbundle`, `residue2_exportbundle`, and `mapping0_exportbundle`.
- Defines `_floor_P` with floor0 and floor1.
- Defines `_residue_P` with residue0, residue1, and residue2.
- Defines `_mapping_P` with mapping0.

Integration points:
- Used by setup/header parsing and synthesis/analysis dispatch.
- Bounds for these arrays are declared in `registry.h`.
- `info.c`, `synthesis.c`, and backend setup code index these arrays after validating backend IDs.

Risk and review signals:
- Minimal static dispatch table.
- Adding backend types requires synchronized updates to `registry.h` bounds and setup/header validation.
- Incorrect ordering would break bitstream backend IDs.

Filesystem relevance:
- No filesystem logic. It is codec backend dispatch registration.
