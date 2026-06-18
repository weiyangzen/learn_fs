# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevbbox.h

## Purpose
Declares the bbox device interface and common structure fields for Ghostscript’s bounding-box accumulator/forwarding device.

## Main Interfaces
- Defines `gx_device_bbox_procs_t`, a virtual proc table for bbox accumulator operations:
  - `init_box`
  - `get_box`
  - `add_rect`
  - `in_rect`
- Declares default implementations for those procs.
- Defines `gx_device_bbox_common`, including forwarding-device fields, bbox procs/data, `white_is_opaque`, current `bbox`, and cached black/white/transparent colors.
- Defines `gx_device_bbox` and its GC descriptor macro `public_st_device_bbox`.

## Exported API
- `gx_device_bbox_init(gx_device_bbox *dev, gx_device *target, gs_memory_t *mem)`
- `gx_device_bbox_fwd_open_close(gx_device_bbox *dev, bool forward_open_close)`
- `gx_device_bbox_set_white_opaque(gx_device_bbox *dev, bool white_is_opaque)`
- `gx_device_bbox_bbox(gx_device_bbox *dev, gs_rect *pbbox)`
- `gx_device_bbox_release(gx_device_bbox *dev)`

## Behavior Contract
- Can be used as a free-standing `bbox` output device or as a component in a forwarding device pipeline.
- Forwarding bbox devices normally propagate open/close to their target, but this can be disabled.
- Non-target bbox devices have an effectively infinite page size; target-backed devices mirror target parameters.
- Custom bbox procs allow subclasses and compositor wrappers to redirect accumulation to shared state.

## Dependencies
Requires `gxdevice.h` and Ghostscript fixed-point/rectangle/device-forwarding types.
