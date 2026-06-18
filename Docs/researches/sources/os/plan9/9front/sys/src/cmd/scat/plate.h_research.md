# File Research: sources/os/plan9/9front/sys/src/cmd/scat/plate.h

Purpose: Older or alternate header declaring DSS plate/image structures and prototypes.

Content:
- Plate parameter enum equivalent to the `sky.h` plate parameter block.
- `Plate`, `Header`, and `Image` structures.
- Global plate/gamma/debug variables.
- Prototypes for plate conversion, DSS reading, q-tree decoding, image generation, and gamma mapping.

Integration: This header overlaps heavily with `sky.h`; the active scat files include `sky.h`, not this file.

Risks:
- Contains stale type declarations: for example `Image* dssread` and `Bitmap* image` differ from the active `Img*` and `Picture*` declarations in `sky.h`.
- If included in new code, it can conflict with current definitions.
