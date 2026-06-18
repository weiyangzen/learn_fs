# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip2.c

Implements a tiled mask clipping device used for pattern rendering. It is structurally based on the mask clip device but treats the mask as a repeating strip bitmap with phase and repetition shift.

Key behavior:
- Defines the `gx_device_tile_clip` procedure table, forwarding most device operations and intercepting fill/copy operations that must respect the tiled mask.
- `tile_clip_initialize` initializes the base mask-clip state from a `gx_strip_bitmap`, records tile parameters, and sets the explicit phase.
- `tile_clip_set_phase` updates the phase used by subsequent tiled mask operations.
- `tile_clip_fill_rectangle` forwards to the target's `strip_tile_rectangle`, using the tile mask as the strip tile and painting only through set bits.
- Computes per-row X offset from phase, repetition height, and tile repetition shift.
- `tile_clip_copy_mono` processes chunks aligned to tile slices, copies tile bits to the scratch memory device, intersects them with source mono data, then forwards the resulting double mask to the target.
- Color, alpha, and RasterOp copy operations scan each row for runs of 1 bits in the tiled mask and forward only those runs to the target.
- The run scanner wraps both X and Y within the tile dimensions and advances tile rows according to tile raster and repetition geometry.

Dependencies:
- Uses `gxclip2.h`, `gxmclip.h` mask-clip storage, memory-device helpers from `gxdevmem.h`, and shared target callbacks from the device procedure table.
- Reuses mask-copy setup macros supplied by the generic mask clipping layer.

Research notes:
- Unlike `gxclipm.c`, this file handles periodic/repeating masks; phase and `rep_shift` are central to aligning pattern tiles with device coordinates.
- Mono copy has a scratch-buffer fast strategy, while color/alpha/RasterOp paths use run enumeration because source pixels cannot be combined with the mask by a simple tile blit.
