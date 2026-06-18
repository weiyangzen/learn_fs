# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gstrans.h

## Purpose
Declares Ghostscript transparency compositor operations, PDF14 compositor parameter structure, transparency source state, graphics-state APIs, imager-level device hooks, and buffer-size estimation macros.

## Public Surface
- `pdf14_compositor_operations`: push/pop device, begin/end group, init/begin/end mask, set blend params.
- `PDF14_OPCODE_NAMES`: debug/display names for opcodes.
- Serialization change bits: `PDF14_SET_BLEND_MODE`, `PDF14_SET_TEXT_KNOCKOUT`, `PDF14_SET_SHAPE_ALPHA`, `PDF14_SET_OPACITY_ALPHA`.
- `gs_transparency_source_t`: constant alpha plus optional mask pointer.
- `gs_pdf14trans_params_t`: all fields needed to transmit a PDF 1.4 transparency operation through a compositor.
- `gs_pdf14trans_t`: compositor object with `gs_composite_common` and PDF14 params.
- Graphics-state transparency APIs and imager-level group/mask APIs.
- `gs_is_pdf14trans_compositor`.
- Buffer estimate macros: `NUM_PDF14_BUFFERS`, `NUM_ALPHA_CHANNELS`, `NUM_COLOR_CHANNELS`, `BITS_PER_CHANNEL`, `ESTIMATED_PDF14_ROW_SIZE`, `ESTIMATED_PDF14_ROW_SPACE`.

## Data Model
- PDF14 params combine operation selector, changed flags, group flags/BBox, channel selector, mask subtype/background/transfer function, blend parameters, opacity/shape sources, and `mask_is_image`.
- The row-space estimate assumes three buffers, one alpha channel, four color channels, and 8 bits per channel.

## Dependencies
Includes `gstparam.h` and `gxcomp.h`, and relies on `gs_state`, `gs_imager_state`, `gx_device`, `gs_rect`, and color/function types from included/forward-declared headers.

## Risks and Notes
- The buffer estimate is explicitly a hack and may underestimate real PDF transparency working space.
- Typo comments (`trasnparency`, `numbe`, `chanels`) do not affect behavior but reflect the vintage/source state.
