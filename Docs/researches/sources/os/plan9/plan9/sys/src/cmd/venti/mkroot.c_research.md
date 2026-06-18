# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/mkroot.c

Purpose: create and write a Venti root block manually.

Behavior:
- Accepts name, type, data score, block size, and previous root score.
- Packs a `VtRoot` and writes it as `VtRootType`.
- Prints the resulting root score.

Integration points:
- Uses Venti client connection and `vtrootpack`.
- Can create Vac-like or other Venti roots when supplied valid fields.

Risks:
- Minimal validation beyond score parsing and numeric blocksize conversion.
