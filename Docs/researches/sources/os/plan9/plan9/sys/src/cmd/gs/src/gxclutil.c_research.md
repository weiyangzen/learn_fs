# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxclutil.c

## Purpose
Provides shared command-list writing utilities: buffered command output, band-list flushing, variable-length integer encoding, compact color encoding, logical-operation/clipping state commands, serialized parameter commands, and filter initializers.

## Public Surface
- `cmd_write_buffer(...)`: writes all pending band and band-range command lists to command and band files.
- `cmd_put_list_op(...)` and `cmd_put_range_op(...)`: reserve command payload space in per-band or range command lists.
- `cmd_size_w` / `cmd_put_w`: variable-length positive integer encoding.
- Color/state helpers: `cmd_put_color`, `cmd_set_tile_colors`, `cmd_set_tile_phase`, `cmd_put_enable_lop`, `cmd_put_enable_clip`, `cmd_set_lop`, `cmd_update_lop`.
- `cmd_put_params(...)`: serializes device parameter lists into an extended command.
- Filter setup helpers: `clist_cfe_init`, `clist_cfd_init`, `clist_rle_init`, `clist_rld_init`.

## Implementation
- Buffers commands in memory as linked `cmd_prefix` chunks grouped by band or band range, flushing to the clist command file plus band index file when the buffer fills.
- Converts low-memory warnings into retryable VM errors unless the writer is configured to ignore such warnings.
- Encodes colors either as full values with trailing zero-byte suppression or as packed byte deltas from the previous color value.
- Handles the special `gx_no_color_index` value as a distinct compact command case.
- Serializes parameter lists into a local buffer when small, otherwise writes directly into reserved command-list space and backs out by shortening the command if serialization fails.

## Dependencies
Uses clist file APIs, command-list state definitions, Ghostscript parameter serialization, RunLength and CCITTFax stream filters, and memory/error helpers.

## Risks and Notes
- Color delta encoding has format-specific packing for odd byte counts; reader and writer must remain exactly synchronized.
- `cmd_put_params` requires the serialized parameter list to fit in the command buffer once reserved.
- Hard file I/O errors make the current clist writer non-retryable; low-memory warnings are deliberately promoted for recovery behavior.

Filesystem relevance: this file writes command-list and band-index data through Ghostscript clist files. It is renderer serialization infrastructure, not filesystem logic.
