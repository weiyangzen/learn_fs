# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclutil.c

Shared command-list writing utilities.

Key behavior:
- Provides debug opcode name tables, per-op statistics, and `cmd_print_stats` under `DEBUG`.
- Writes buffered command lists to command and band files via `cmd_write_band` and `cmd_write_buffer`.
- Manages command buffer allocation/alignment and per-band/range command list linkage in `cmd_put_list_op` and `cmd_put_range_op`.
- Encodes variable-length integers with `cmd_size_w`/`cmd_put_w`.
- Defines color selector descriptors for color0, color1, tile color0, and tile color1.
- Encodes colors either as full values with omitted trailing zero bytes or as compact deltas, including special handling for `gx_no_color_index`.
- Emits commands for tile colors, tile phase, logical operation enable/disable, clipping enable/disable, logical operation value, and serialized parameter lists.
- Initializes CCITTFax encode/decode and RunLength encode/decode stream states for command-list compression.

Notable dependencies:
- Clist writer structures, command formats, stream filter templates, parameter serialization, and path-command statistics.

Research notes:
- This file is central write-side infrastructure used by rectangle/path/image command emitters.
- Low-memory warnings may be converted into retryable VM errors unless the writer is configured to ignore them.
- Color delta encoding is carefully tied to `gx_color_index` byte width and device depth; reader decoding in `gxclrast.c` mirrors it.
