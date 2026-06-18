# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngwio.c

Provides libpng write-side output callback plumbing.

Key points:
- Compiles under `PNG_WRITE_SUPPORTED`.
- `png_write_data()` is the internal write dispatcher:
  - Calls `png_ptr->write_data_fn` when configured.
  - Raises `png_error` on a NULL write function.
- `png_default_write_data()` is available when stdio is enabled:
  - Uses `fwrite()` for normal C streams.
  - Uses `WriteFile()` on Windows CE.
  - Raises `png_error("Write Error")` if fewer bytes are written than requested.
- Under `USE_FAR_KEYWORD`, the default writer copies far buffers through a fixed near stack buffer before writing, supporting old segmented memory models.
- `png_flush()` calls `png_ptr->output_flush_fn` when flush support is enabled.
- `png_default_flush()` flushes the stdio stream with `fflush()` when not on Windows CE.
- `png_set_write_fn()` installs the output `io_ptr`, write callback, and optional flush callback:
  - Falls back to default stdio writer/flush functions when callbacks are NULL and stdio is available.
  - Clears any existing read callback and warns if the same `png_struct` was configured for both reading and writing.
- `png_far_to_near()` converts far pointers to near pointers for supported old compiler/memory-model combinations and can validate that the segment was not lost.

Dependencies and interactions:
- Uses `png_struct` callback fields: `io_ptr`, `write_data_fn`, `output_flush_fn`, and `read_data_fn`.
- Called by higher-level chunk and IDAT writers through `png_write_data`.
- Used by `png_create_write_struct()` / `png_write_init_*()` to establish default output behavior.

Research relevance:
- This file is the writer output abstraction boundary. Applications using non-stdio output replace behavior here via `png_set_write_fn()` rather than modifying chunk-writing code.
