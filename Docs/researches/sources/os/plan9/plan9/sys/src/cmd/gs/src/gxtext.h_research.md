# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtext.h

Internal support header for Ghostscript driver text enumeration and rendering.

Key contents:
- Defines `gs_text_returned_t`, carrying current character/glyph for intervention and accumulated width for width-returning operations.
- Defines composite font stack types `gx_font_stack_item_t` and `gx_font_stack_t`, with `MAX_FONT_STACK` set to 5.
- Defines `gs_text_enum_common`, the shared prefix for text enumerator implementations. It stores immutable text-begin arguments, device/imaging device, imager state, original/current fonts, path/color/clip data, memory, procedure table, reference count, scaling/cache information, composite font stack, CID/FMapType state, grid-fitting flag, and returned data.
- Defines concrete `struct gs_text_enum_s` as the common structure.
- Declares `gs_text_enum_init` and `gs_text_enum_copy_dynamic`.
- Provides `SHOW_IS*` macros for operation flag checks such as drawing, stringwidth, intervention, replacement widths, and slow show cases.
- Defines `gs_text_enum_procs_t`, the virtual method table for text enumeration: `resync`, `process`, `is_width_only`, `current_width`, `set_cache`, `retry`, and `release`.
- Declares default release procedure `gx_default_text_release`.

Notable dependencies:
- Public text parameters from `gstext.h`.
- Reference counting from `gsrefct.h`.

Research notes:
- The `imaging_dev` field is a documented workaround for forwarding devices such as bbox devices, allowing lower-level drawing operations to be redirected for bounding-box accounting.
- The comments spell out required behavior for text processing: charpath/width path appending, intervention after characters, current-font reset, and width reporting.
- Implementations must call `rc_free_text_enum` from their freeing procedure so device and other referenced structures are released correctly.
