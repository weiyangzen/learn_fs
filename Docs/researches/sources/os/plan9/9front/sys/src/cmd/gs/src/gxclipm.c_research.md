# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclipm.c

Implements a one-bit mask clipping device. It clips drawing operations through a finite bitmap mask and forwards visible runs or mask intersections to the target device.

Key behavior:
- Defines the exported `gs_mask_clip_device` procedure table, intercepting fills, bitmap copies, strip tiling, RasterOp strip copy, and clipping-box queries.
- `mask_clip_fill_rectangle` clips the requested rectangle to the finite mask extents, then forwards a `copy_mono` through the mask bits using the requested fill color.
- Uses `FIT_MASK_COPY` to convert target coordinates into mask coordinates, clamp to mask bounds, and adjust source data/source X when the requested operation starts before the mask.
- `mask_clip_copy_mono` combines source mono data with mask bits in a scratch memory device, then forwards the resulting mask to the target.
- `clip_runs_enumerate` scans mask rows using byte run-length lookup tables, finds contiguous 1-bit runs, and coalesces identical runs on adjacent rows into vertical rectangles.
- Copy color, copy alpha, strip tile rectangle, and strip copy RasterOp use `clip_runs_enumerate` with the shared callbacks from `gxclip.c`.
- `mask_clip_get_clipping_box` forwards the target clipping box and offsets it by the mask phase.

Dependencies:
- Uses `gxclipm.h`, `gxmclip.h`, `gxclip.h` callback helpers, bit-run tables from `gsbittab.h`, and memory-device support from `gxdevmem.h`.

Research notes:
- The mask is finite, not repeating; all operations are clipped against `tiles.size`.
- Run coalescing reduces callback volume for vertically aligned opaque mask regions.
- The mono path differs from other copy paths because it can cheaply intersect two 1-bit sources before forwarding.
