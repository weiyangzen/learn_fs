# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstrans.h

Declares PDF 1.4 transparency compositor operations, parameter structures, graphics-state accessors, and imager-level device hooks.

Key definitions:
- `pdf14_compositor_operations` covers push/pop device, begin/end group, init/begin/end mask, and set blend params.
- Serialization change bits identify blend mode, text knockout, shape alpha, and opacity alpha changes.
- `gs_transparency_source_t` pairs constant alpha with an optional transparency mask.
- `gs_pdf14trans_params_t` carries all operation-specific PDF14 compositor data.
- `gs_pdf14trans_t` embeds `gs_composite_common` plus PDF14 params.
- Estimated buffer-space macros approximate PDF14 transparency row memory using three buffers, one alpha channel, four color channels, and 8 bits per channel.

Public API:
- Blend/alpha/text-knockout accessors.
- PDF14 device push/pop.
- Transparency group and mask begin/end/init/discard calls.
- Imager-level group/mask calls and compositor identification.

Research notes:
- The row-space estimate is explicitly a hack and may underpredict real transparency buffer needs.
