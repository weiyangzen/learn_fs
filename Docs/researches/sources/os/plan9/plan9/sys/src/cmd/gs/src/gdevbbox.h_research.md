# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevbbox.h

Public interface and structure definition for Ghostscript's bounding-box accumulator device.

Key contents:
- Documents two usage modes: standalone `bbox` output device and embedded C component in a device pipeline.
- Declares `gx_device_bbox_procs_t`, a virtual procedure table for bbox initialization, retrieval, rectangle addition, and containment tests.
- Declares default implementations: `bbox_default_init_box`, `bbox_default_get_box`, `bbox_default_add_rect`, and `bbox_default_in_rect`.
- Defines `gx_device_bbox_common`, embedding forwarding-device state plus bbox-specific fields: standalone/forward-open-close flags, box procedures, box procedure data, white-opacity mode, current bbox, mapped black/white, and transparent color.
- Declares GC descriptor support through `public_st_device_bbox`.
- Exposes lifecycle/configuration APIs:
  - `gx_device_bbox_init`
  - `gx_device_bbox_fwd_open_close`
  - `gx_device_bbox_set_white_opaque`
  - `gx_device_bbox_bbox`
  - `gx_device_bbox_release`

Notable dependencies:
- Requires Ghostscript core device definitions from `gxdevice.h` before inclusion.
- Uses Ghostscript fixed-point geometry and memory/device types.

Research notes:
- The header explicitly notes that bbox devices unusually may propagate `open_device` and `close_device` to their target.
- `gx_device_bbox_bbox` reports in 1/72 inch user units, not raw fixed device pixels.
- The virtual bbox procedure table supports subclass/compositor sharing, which is used by `gdevbbox.c` for composited forwarding devices.
