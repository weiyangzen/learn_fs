# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclipm.c

## Purpose
Implements the general bitmap-mask clipping device. It forwards drawing operations only where a finite mask bitmap has set bits.

## Main Responsibilities
- Defines exported `gs_mask_clip_device`.
- Clips rectangle fills by painting through the mask with `copy_mono`.
- Clips bitmap copy operations by intersecting source data with the mask.
- Enumerates mask runs for color, alpha, strip-tile, and RasterOp operations.
- Computes a clipping box adjusted by mask phase.

## Key Implementation Details
- `FIT_MASK_COPY` maps requested target coordinates into mask coordinates and clips them to the mask bitmap extent.
- `mask_clip_copy_mono` uses a memory-device buffer to combine the source bitmap and mask bitmap.
- `clip_runs_enumerate` scans mask bytes using `byte_bit_run_length` tables.
- Consecutive identical horizontal runs on adjacent scanlines are coalesced into vertical rectangles before callback forwarding.
- Callback forwarding reuses `clip_call_*` functions from `gxclip.c`.

## Important Edge Cases
- Operations outside the mask bounds are clipped to empty by `FIT_MASK_COPY`.
- `copy_mono` uses color inversion choices from `setup_mask_copy_mono`.
- `mask_clip_get_clipping_box` forwards the target clipping box and subtracts mask phase.

## Dependencies
- `gxclipm.h` for exported device declaration.
- `gxclip.h` callback routines indirectly through `gxmclip.h`.
- `gsbittab.h` for bit-run lookup tables.
- `gxdevmem.h` for temporary mask intersection buffers.

## Research Notes
This is the finite-mask counterpart to `gxclip2.c`. It scans actual mask rows once rather than repeating a tile pattern.
