# File Research: sources/os/plan9/9front/sys/src/cmd/gs/libpng/pngmem.c

## Role

`pngmem.c` centralizes libpng 1.2.8 memory allocation for the bundled Ghostscript/libpng copy in the 9front source tree. It provides allocation, deallocation, overflow-checked memory helper wrappers, and optional user-provided allocator hooks.

## Main APIs and Behavior

- `png_create_struct()` / `png_create_struct_2()` allocate and zero either `png_struct` or `png_info`.
- `png_destroy_struct()` / `png_destroy_struct_2()` free structs allocated by the create helpers.
- `png_malloc()` delegates to a custom allocator when `PNG_USER_MEM_SUPPORTED` is enabled, otherwise falls back to `png_malloc_default()`.
- `png_malloc_default()` handles standard allocation and platform-specific variants:
  - Borland DOS `farmalloc` / `farfree`.
  - MSVC `halloc` / `hfree` under `MAXSEG_64K`.
  - normal `malloc` / `free`.
- `png_free()` delegates to custom `free_fn` when present.
- `png_malloc_warn()` temporarily allows allocation failure to return `NULL` with warning behavior instead of fatal `png_error`.
- `png_memcpy_check()` and `png_memset_check()` guard 32-bit `png_uint_32` lengths against truncation to `png_size_t`.
- `png_set_mem_fn()` and `png_get_mem_ptr()` expose user allocator state when enabled.

## Notable Implementation Details

This file has a large legacy Borland 16-bit DOS branch. It special-cases exact 64 KiB allocation because old segmented memory allocators could return non-normalized pointers that zlib could not use. That branch maintains an `offset_table` inside `png_struct` and hands out fixed 64 KiB blocks from it.

The normal branch is much simpler: it validates `png_ptr`, rejects zero-size allocation, checks representability of `png_uint_32 size` in the platform allocation type, allocates memory, and raises `png_error` unless `PNG_FLAG_MALLOC_NULL_MEM_OK` is set.

## Dependencies

- Public/internal libpng declarations from `png.h`.
- C runtime allocation APIs.
- Platform-specific memory APIs controlled by compile-time macros.
- `png_error()` / `png_warning()` for fatal and nonfatal allocator failures.

## State Mutated

- `png_ptr->mem_ptr`, `malloc_fn`, `free_fn` for custom allocation.
- `png_ptr->flags` temporarily in `png_malloc_warn()`.
- Borland branch fields: `offset_table`, `offset_table_ptr`, `offset_table_number`, `offset_table_count`, `offset_table_count_free`.

## Risks and Maintenance Notes

- This is old libpng 1.2.8 allocation code with many legacy platform branches that are likely irrelevant on Plan 9/9front but still affect portability if macros change.
- The `PNG_MAX_MALLOC_64K` path in the normal branch contains a suspicious conditional spelling: `if(png_ptr->flags&PNG_FLAG_MALLOC_NULL_MEM_OK) == 0)`. If that preprocessor path is enabled, it appears syntactically invalid as read.
- User allocator hooks must match libpng’s expectations exactly; allocation failure can be fatal depending on flags.
- `png_malloc_warn()` assumes `png_ptr` is valid and directly reads/writes `png_ptr->flags`.

## Research Summary

This file is the allocator substrate for all read/transform files in this group. The rest of the reader relies on these wrappers for row buffers, zlib buffers, text chunks, gamma tables, palette lookup tables, and progressive-save buffers.
