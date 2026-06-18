# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclrast.c

## Purpose
Implements the Ghostscript command-list interpreter/rasterizer. It reads compact command streams for selected bands or saved pages, reconstructs graphics state, color state, paths, clipping, images, halftones, compositors, and bitmap operands, then dispatches equivalent drawing operations to a target device.

## Public Surface
- `clist_playback_band(...)`: main playback engine used by command-list readers to render or set up from a filtered band stream.

## Implementation
- Maintains an aligned command buffer with refill helpers, variable-length integer decoding, and direct stream reads for payloads larger than the current buffer contents.
- Decodes compact rectangle, tile, color, delta-color, copy-mono/color/alpha, RasterOp, path segment, path paint, image, clipping, color-space, halftone, compositor, and parameter commands.
- Reconstructs per-band `gx_clist_state`, tile cache references, tile phases, drawing colors, logical operations, image enumerators, and a local `gs_imager_state`.
- Decompresses bitmap/tile data using RunLength or CCITTFax decode helpers and expands short scanlines into device raster alignment when needed.
- Handles clipping commands by accumulating clipping marks into `gx_device_cpath_accum`, then re-enabling clipping only when the resulting clip does not contain the whole target box.
- Supports command-list compositors by deserializing a compositor id/payload, creating a compositor device over the current target, and invoking compositor read-update hooks.

## Dependencies
Uses most of the Ghostscript graphics core: command-list structures from `gxcldev.h`, paths and clip paths, imager state, device colors, color spaces, images, halftones, serialization, stream filters, compositors, and device drawing procedures.

## Risks and Notes
- Bad or inconsistent command bytes become fatal errors after dumping buffer context.
- Several paths trust command-list invariants established by writer-side code, such as decompressed bitmap payloads fitting the command buffer.
- Indexed color-space data and large image data may allocate transient heap buffers; cleanup is centralized at the `out` label.
- Alpha copy explicitly cannot combine with RasterOp in this implementation.
- The `read_create_compositor` format has no independent total length field and relies on the design assumption that compositor command payloads fit in the command buffer.

Filesystem relevance: this is band-list playback for Ghostscript rendering. It reads command-list streams, including band files through callers, but does not implement filesystem semantics.
