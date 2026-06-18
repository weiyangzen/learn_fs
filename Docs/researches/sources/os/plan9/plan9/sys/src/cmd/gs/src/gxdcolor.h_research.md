# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxdcolor.h

Defines the internal device-color object model.

- Introduces `gx_rop_source_t`, the source bitmap/color descriptor used by RasterOp paths.
- Provides `gx_rop_no_source_body`, `gx_rop_source_set_color`, and `gx_set_rop_no_source` helpers.
- Defines `gx_device_color_type_s`, the method table for device color variants.
- Device-color methods include:
  - `save_dc`
  - `get_dev_halftone`
  - `get_phase`
  - `load`
  - `fill_rectangle`
  - `fill_masked`
  - `equal`
  - `write`
  - `read`
  - `get_nonzero_comps`
- Documents command-list serialization rules in detail:
  - `write` may emit no bytes if the saved color already matches.
  - `read` reconstructs the color and may receive the same `pdevc` and `prior_devc`.
  - Device halftones are serialized separately as all-band commands.
- Declares standard device color type records:
  - none, null, pure, binary halftone, colored halftone, WTS.
- Exports nonzero-component helpers for pure and halftone colors.
- Provides macros for:
  - remapping device color
  - loading halftone/pattern cache
  - filling rectangles through a device color
- Declares `gx_dc_write_color` and `gx_dc_read_color`.

Role in subsystem: central polymorphic contract between high-level graphics state colors and low-level device rendering operations.
