# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclpath.h

Defines high-level command-list opcodes, known-state masks, path-segment encodings, and exported helpers for path/image/color command writing.

Key behavior:
- Defines per-band known-state flags for line parameters, flatness, fill adjust, CTM, dash, clip path, color space, alpha/opacity, overprint/blend/text knockout, and related misc state.
- Defines drawing-color categories used by command serialization.
- Extends the command-list opcode space with misc graphics-state commands, image commands, path segment commands, path paint commands, and extended commands.
- Defines extended opcodes for serialized parameter lists, compositor creation, halftone data, halftone segments, and serialized drawing colors.
- Provides opcode name string macros and operand-count metadata used by debugging/decoding code.
- Documents variable-length relative fixed-point coordinate encodings for compact path deltas.
- Defines `cbuf_ht_seg_max_size` for maximum halftone segment payload inside the command buffer.
- Declares clist driver procedures for fill/stroke path, parallelogram fill, and triangle fill.
- Provides helper macros for comparing/updating cached imager-state members.
- Declares exported writer helpers for colors-used calculation, slow-ROP detection, drawing-color serialization, known-state clearing, CTM serialization, unknown-state emission, and clip-path dirty checking.

Dependencies:
- Extends `gxcldev.h` and expects command-buffer macros, `gx_device_clist_writer`, `gx_clist_state`, `gx_drawing_color`, `gx_clip_path`, `gs_matrix`, and related Ghostscript graphics types.

Research notes:
- The opcode layout reserves ranges for misc commands, segment commands, path commands, and extended commands; changing values would break command-list reader compatibility.
- `cmd_max_dash` limits which strokes can remain path commands; longer dashed strokes must be converted/fallback elsewhere.
- `is_bits` is central to compact path encoding because it chooses the smallest valid fixed-point delta representation.
