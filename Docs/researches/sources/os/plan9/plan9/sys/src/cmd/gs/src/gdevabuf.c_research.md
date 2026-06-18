# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevabuf.c

Alpha and alpha-buffer memory devices.

Key points:
- `gs_make_mem_alpha_device` creates a 2-bit or 4-bit alpha-capable memory device by patching a standard memory device descriptor.
- Reimplements color mapping so nonzero target colors map to maximum alpha or alpha-derived values.
- Implements alpha copying through fill/copy-color behavior.
- `gs_make_mem_abuf_device` creates an oversampled alpha-buffer device that accumulates high-resolution bits and flushes compressed alpha rows to a lower-resolution target.
- `gs_device_is_abuf` identifies the alpha-buffer device by device-name identity.
- Maintains a sliding Y-window over a limited-height band buffer to avoid copying while processing top-to-bottom bands.
- `abuf_flush_block` computes a bounding box, compresses scaled bits into alpha data, and forwards to the target device’s `copy_alpha`.
- `mem_abuf_copy_mono` and `mem_abuf_fill_rectangle` map incoming operations into the sliding buffer.
- `mem_abuf_close` flushes before closing.
- `mem_abuf_get_clipping_box` scales the target clipping box up by the supersampling scale.

Dependencies and interactions:
- Uses Ghostscript memory device internals from `gxdevmem.h` and `gdevmem.h`.
- Calls bit helpers such as `bits_bounding_box` and `bits_compress_scaled`.
- Intended for antialiased text/graphics and masked image cases with constrained band-order assumptions.

OS/filesystem relevance:
- None; in-memory rendering device support.
