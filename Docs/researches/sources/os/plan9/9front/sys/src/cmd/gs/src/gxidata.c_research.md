# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxidata.c

## Role

`gxidata.c` implements generic ImageType 1 image row enumeration, unpack/repack dispatch, renderer invocation, flush handling, image-device setup, and cleanup.

This is image enumeration/rendering infrastructure, not filesystem code.

## Main Functions

- `gx_image1_plane_data`: processes incoming image planes row by row, unpacks or repacks source data, advances DDA state, applies clipping prechecks, and calls the selected renderer.
- `gx_image1_flush`: sends the renderer a `height == 0` flush call for buffered data.
- `update_strip`: translates strip DDAs to the current row origin and resets pixel DDA state.
- `repack_bit_planes`: combines 1 to 8 one-bit source planes into byte-wide samples using lookup tables and spread.
- `setup_image_device`: wraps the target device with clipping and RasterOp forwarding devices when present.
- `gx_image1_end_image`: optionally flushes, releases scaler state, frees clip/rop devices, buffers, line storage, and the image enumerator.

## Important Behavior

- Tracks partial progress with `penum->used.x` and `penum->used.y` so rendering can resume after an error/interruption.
- Handles bit-planar input separately from chunky/multi-component plane input.
- Uses direct source data when possible, but unpacks into `penum->buffer` when expansion or multiple planes are needed.
- Computes integer row/column coverage for portrait and landscape postures before invoking non-interpolated renderers.
- Null bit planes are represented by a zero block in the destination buffer to avoid per-bit conditional tests.

## Dependencies And Integration

- Uses `gx_image_enum`, `gx_image_plane_t`, sample unpack procedures, sample lookup tables, DDA helpers, clip/ROP forwarding devices, and image scaler release hooks.
- Calls `gx_image_flush`/`gx_image1_flush` and renderer procedure pointers selected by image classes.

## Notable Risks

- `BCOUNT` combines width, data offset, samples per pixel, bits per sample, and plane count; mistakes in plane metadata can under/over-read rows.
- `repack_bit_planes` writes in groups of eight output bytes and relies on caller-provided padding/alignment in the image buffer.
- Error recovery manipulates DDA state and `used` counters; small changes can break resumability.
- `gx_image1_end_image` frees the enumerator itself, so callers must not touch it afterward.
