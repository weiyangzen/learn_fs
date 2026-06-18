# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.c

Implements transparency graphics-state accessors and non-rendering PDF 1.4 transparency compositor dispatch.

Key behavior:
- Sets/gets blend mode, opacity alpha, shape alpha, and text knockout, clamping alpha to `[0,1]` and validating blend modes.
- Exposes current transparency stack type.
- Defines a dummy transparency-stack descriptor and pop helper; actual push helper is disabled by `PUSH_TS 0`.
- `gs_state_update_pdf14trans` sends `gs_pdf14trans_params_t` operations to `send_pdf14trans` and installs a new compositor device if one is returned.
- Initializes and begins/ends transparency groups by filling PDF14 compositor params with isolation, knockout, alpha, shape, blend mode, and bbox.
- Imager-level `gx_begin/end_transparency_group` call device transparency procs when present.
- Initializes mask params with identity transfer by default.
- Begins transparency masks by copying background data, sampling the transfer function into 256 byte values, and forwarding PDF14 params.
- Imager-level mask begin/end/init functions call device procs or clear opacity/shape masks.
- Provides PDF14 push/pop device operations.

Dependencies:
- Uses graphics state internals, device compositor support, PDF 1.4 device interface (`gdevp14.h`), and transparency parameter definitions.

Research notes:
- Group color space is logged but not used; blending color space is currently based on the process color model of the output device.
- `gs_discard_transparency_layer` is marked dummy/NYI and operates on the disabled local stack mechanism.
