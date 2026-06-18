# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclpath.h

## Purpose
Defines extended command-list opcodes, state-known flags, and exported helpers for path-level command-list writing.

## Main Responsibilities
- Defines per-band known-state bit flags.
- Defines drawing-color classification enum `cmd_dc_type`.
- Extends the command set for imager state, clipping, images, path segments, path painting, and extension commands.
- Documents compact path operand encoding.
- Declares clist path driver procedures and support helpers.

## Key Definitions
Known-state flags include:
- line cap/join
- curve/stroke adjustment
- flatness
- line width
- miter limit
- overprint/blend/text-knockout
- opacity and shape alpha
- fill adjustment
- CTM
- dash
- clip path
- color space

Extended command opcodes include:
- `cmd_opv_set_fill_adjust`
- `cmd_opv_set_ctm`
- `cmd_opv_set_color_space`
- `cmd_opv_set_misc2`
- `cmd_opv_set_dash`
- clip enable/disable/begin/end
- image begin/data commands
- path segment commands
- fill/eofill/stroke/polyfill commands

Further extension opcodes include:
- serialized parameter list
- compositor creation
- halftone data
- drawing-color serialization

## Exported Helpers
- `cmd_drawing_colors_used`
- `cmd_slow_rop`
- `cmd_put_drawing_color`
- `cmd_clear_known`
- `cmd_write_ctm_return_length`
- `cmd_write_ctm`
- `cmd_write_unknown`
- `cmd_check_clip_path`

## Dependencies
- Extends `gxcldev.h`.
- Relies on command-buffer sizing and encoding helpers from lower-level clist infrastructure.

## Research Notes
This header is the opcode/state contract for `gxclpath.c` and related command-list image/path writers. The comments encode the wire format, making this file essential for reader/writer compatibility.
