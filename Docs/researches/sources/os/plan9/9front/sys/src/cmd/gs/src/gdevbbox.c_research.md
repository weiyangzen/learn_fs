# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.c

## Purpose
Implements Ghostscript’s `bbox` device, a forwarding or stand-alone device that accumulates the drawn page bounding box. In stand-alone mode it prints `%%BoundingBox` and `%%HiResBoundingBox`; in pipeline mode it forwards rendering to a target while tracking drawing extents.

## Main Interfaces
- Defines the public `gs_bbox_device` prototype.
- Implements default bbox proc set: `bbox_default_init_box`, `bbox_default_get_box`, `bbox_default_add_rect`, `bbox_default_in_rect`.
- Implements exported helpers declared in `gdevbbox.h`: `gx_device_bbox_init`, `gx_device_bbox_fwd_open_close`, `gx_device_bbox_set_white_opaque`, `gx_device_bbox_bbox`, `gx_device_bbox_release`.
- Overrides many device drawing procedures: rectangle fill, mono/color/alpha copy, path fill/stroke, masks, trapezoids, parallelograms, triangles, thin lines, strip tiling/ROP, typed images, compositors, and text.

## Behavior
- Stores accumulated extents in fixed device coordinates, then converts them back to 1/72 inch user-style coordinates in `gx_device_bbox_bbox`.
- Treats white as transparent unless `WhiteIsOpaque` is set, using `transparent` to suppress bbox growth for transparent/white fills.
- Full-page rectangle or strip-tile operations call `BBOX_INIT_BOX`; this can reset the bbox on page erases depending on transparency/white behavior.
- If a target exists, most operations first forward to the target, then update the bbox.
- For clipped high-level operations, it temporarily sets `bdev->target = NULL` and asks default Ghostscript drawing routines to decompose the drawing through the clipping path so the bbox is accurate.
- For unclipped paths/images, it often uses path/image transformed bounding boxes directly for speed.
- Typed image handling wraps a target image enumerator and accumulates the transformed bbox for each image data chunk.
- Compositor creation wraps target compositor devices with a new bbox forwarding device that shares the original bbox accumulator.
- `bbox_text_begin` uses the default text path but points the text enumerator’s imaging device back at the bbox device when forwarding.

## Parameters
- `get_params` reports `PageBoundingBox` and `WhiteIsOpaque`.
- `put_params` accepts `PageBoundingBox` to seed/reset the accumulator and `WhiteIsOpaque` to change transparency semantics, then forwards other parameters.

## Dependencies
Uses Ghostscript core device, path, clip, image, imager, and drawing-color APIs: `gxdevice.h`, `gsdevice.h`, `gxdcolor.h`, `gxiparam.h`, `gxistate.h`, `gxpaint.h`, `gxpath.h`, `gxcpath.h`.

## Notes
- The bbox device uses a very high default resolution and huge page coordinate range to avoid limiting real-device jobs.
- There is a suspicious call in `bbox_draw_thin_line`: the target call passes `fx0, fy0, fx1, fy0` rather than `fx0, fy0, fx1, fy1`; this may be intentional legacy behavior or a typo worth verifying before modifying.
