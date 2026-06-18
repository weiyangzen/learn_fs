# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcgml.c

Implementation of the local CGM-writing library used by the CGM Ghostscript device.

Key responsibilities:
- Allocates and initializes `cgm_state`, including metafile defaults, picture defaults, control attributes, graphics attributes, and command buffer state.
- Implements public CGM API calls for metafile, picture, control, graphical primitive, and attribute elements.
- Serializes CGM binary command headers and command continuation chunks.
- Serializes CGM data types: integers, fixed reals, VDCs, points, strings, indexed/direct colors, RGB triples, and cell arrays.
- Tracks selected CGM state values in `cgm_state` after writing corresponding commands.

Important behavior:
- Commands are accumulated in a fixed 400-byte buffer and flushed with short or extended CGM command headers.
- `write_command` pads writes to an even byte count as required by CGM binary encoding.
- `cgm_CELL_ARRAY` always emits packed cell arrays, ignoring the caller's requested representation mode.
- `cgm_CELL_ARRAY` handles bit-aligned source offsets by combining adjacent bytes.
- Fixed real serialization floors negative values before writing whole/fraction parts.
- State-setting calls generally both write the CGM element and update `st`.
- Termination only frees the state object; metafile/picture closure is the caller's responsibility.

Dependencies:
- Internal definitions from `gdevcgmx.h` and public types from `gdevcgml.h`.
- Uses caller-provided allocator and output `FILE *`.

Notable risks:
- `cgm_set_metafile_elements` handles `cgm_set_COLOR_PRECISION` by writing `meta->color_precision` but assigns `st->metafile.color_index_precision` instead of `st->metafile.color_precision`.
- `cgm_POLYGON_SET` starts `OP(POLYGON)` instead of `OP(POLYGON_SET)`, so it may emit the wrong CGM primitive opcode.
- `put_string` uses `put_int(st, 65535, 2)` for extended string chunk length; `put_int` only handles 8/16/24/32 precision, so very long strings are likely malformed.
- Floating real representation is unimplemented in `put_real`.
- Most public functions do little range/state validation and rely on callers to maintain valid CGM sequencing.
- `cgm_CELL_ARRAY` reads `row[i + 1]` when shifting misaligned data, so callers must provide an accessible extra byte past each row's logical packed length.
