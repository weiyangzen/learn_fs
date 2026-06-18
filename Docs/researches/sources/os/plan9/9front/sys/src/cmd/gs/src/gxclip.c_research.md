# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclip.c

Implements Ghostscript's path/rectangle-list clipping device. It wraps a target device and intercepts drawing operations, splitting each request into sub-rectangles covered by a clip list before forwarding to the target.

Key behavior:
- Defines the `gx_device_clip` procedure table, forwarding non-drawing operations and intercepting rectangle fill, bitmap copy, alpha copy, fill mask, strip tile, RasterOp strip copy, clipping-box queries, and get-bits-rectangle.
- Builds clipping devices with `gx_make_clip_translate_device`, copying the supplied clip list and recording a device-space translation; `gx_make_clip_path_device` derives the list from a clip path.
- Maintains a cursor into the sorted clip-rectangle list to make repeated nearby clipping checks cheaper.
- `clip_enumerate` handles the fast path where the requested rectangle lies wholly inside the current clip rectangle.
- `clip_enumerate_rest` walks the rectangle list, intersects each clip rectangle with the requested target rectangle, and invokes a callback for every visible fragment.
- Includes optional vertical-strip coalescing for full-width fragments, mainly useful for rotated images or near-vertical drawing through convex clips.
- `clip_fill_rectangle` open-codes common one-rectangle cases before falling back to generic enumeration.
- Copy/mask/tile/RasterOp operations share the same enumeration callback structure and adjust source pointers/source X offsets according to the clipped fragment.
- `clip_get_clipping_box` lazily intersects the target device box with the clip-list outer bounds, then translates it back into client coordinates.
- `clip_get_bits_rectangle` forwards readback to the target while translating request and unread rectangles.

Dependencies:
- Uses Ghostscript device procedure tables from `gxdevice.h`, clipping definitions from `gxclip.h`, and clip-path/list accessors from `gxcpath.h`.
- Relies on `gx_clip_list`, `gx_clip_rect`, `gx_device_clip`, `gx_clip_path`, fixed/int rectangle helpers, and standard device forwarding procedures.

Research notes:
- Correctness depends on the clip list being sorted by Y and linked with expected head/tail behavior; the cursor-warp logic assumes this structure.
- The callbacks intentionally pass target coordinates, not client coordinates, after applying `translation`.
- Several callback helpers are non-static because `gxclipm.c` reuses them for mask-run clipping.
