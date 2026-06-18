# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/libpng/pngmem.c

## Purpose

`pngmem.c` is libpng 1.2.8's centralized memory allocation layer. It provides allocation and free entry points for `png_struct`, `png_info`, generic libpng buffers, overflow-checked memory operations, and optional application-provided allocator hooks.

This is vendored third-party libpng code inside Plan 9's Ghostscript tree, not Plan 9 filesystem logic.

## Main Responsibilities

- Allocate zeroed `png_struct` and `png_info` objects via `png_create_struct()` / `png_create_struct_2()`.
- Free those objects via `png_destroy_struct()` / `png_destroy_struct_2()`.
- Allocate and free generic libpng memory via `png_malloc()`, `png_malloc_default()`, `png_malloc_warn()`, `png_free()`, and `png_free_default()`.
- Support user-defined allocation callbacks when `PNG_USER_MEM_SUPPORTED` is enabled.
- Support legacy 16-bit Borland/DOS memory models, including special handling for 64K zlib allocations.
- Provide overflow-checking wrappers `png_memcpy_check()` and `png_memset_check()`.
- Expose `png_set_mem_fn()` and `png_get_mem_ptr()` for application allocator state.

## Key Control Flow

The file has two major compile-time branches:

- Borland DOS special handler: active for `__TURBOC__ && !defined(_Windows) && !defined(__FLAT__)`.
- Normal handler: used by modern/flat builds, including the expected Plan 9 build path unless these legacy macros are set.

In the normal path:

- `png_create_struct()` delegates to `png_create_struct_2()` when user memory is enabled.
- `png_create_struct_2()` chooses the allocation size from `PNG_STRUCT_INFO` or `PNG_STRUCT_PNG`, then allocates with user malloc, `farmalloc`, `halloc`, or `malloc`, depending on compile-time platform macros.
- `png_malloc()` validates `png_ptr` and size, dispatches to user malloc if present, otherwise calls `png_malloc_default()`.
- `png_malloc_default()` rejects null pointers and zero-size requests, optionally rejects allocations over 64K, checks whether `png_uint_32 size` can fit into the platform allocation type, then allocates.
- `png_free()` dispatches to a user free callback if present, otherwise to `png_free_default()`.
- `png_malloc_warn()` temporarily sets `PNG_FLAG_MALLOC_NULL_MEM_OK` so allocation failure returns `NULL` instead of raising a fatal libpng error.

## Legacy 64K Handling

The Borland-specific path handles a historical zlib issue where exactly 64K allocations may not be returned on a segment boundary. If a 64K allocation cannot be used directly, it allocates a larger table, aligns it, and hands out fixed 64K blocks through `png_ptr->offset_table_ptr`.

This path tracks:

- `offset_table`
- `offset_table_ptr`
- `offset_table_number`
- `offset_table_count`
- `offset_table_count_free`

Freeing one of these special blocks increments the free count; when all handed-out blocks are freed, the backing table and pointer table are released.

## Important Data and Dependencies

Depends on definitions from `png.h`, especially:

- `png_struct`, `png_info`
- `png_malloc_ptr`, `png_free_ptr`
- `PNG_FLAG_MALLOC_NULL_MEM_OK`
- `PNG_MAX_MALLOC_64K`
- `PNG_USER_MEM_SUPPORTED`
- `png_error()`, `png_warning()`
- `png_memset`, `png_memcpy`

The allocator is shared across libpng read, write, transform, chunk, and metadata paths.

## Error Handling

Allocation failures usually call `png_error()` unless `PNG_FLAG_MALLOC_NULL_MEM_OK` is set. `png_malloc_warn()` is the non-fatal allocation helper used by callers that can degrade gracefully.

`png_memcpy_check()` and `png_memset_check()` convert `png_uint_32` lengths to `png_size_t` and raise `png_error()` if the cast truncates, preventing overflow on platforms where `png_size_t` is narrower.

## Notable Observations

- The file is heavily portability-oriented and includes obsolete DOS/Windows memory model support.
- Under the normal `PNG_MAX_MALLOC_64K` / no-user-memory branch, the source contains a syntactically suspicious condition:
  `if(png_ptr->flags&PNG_FLAG_MALLOC_NULL_MEM_OK) == 0)`.
  If that compile-time branch is enabled as-is, it appears malformed.
- The normal allocation path does not zero buffers returned by `png_malloc()`, only structures allocated by `png_create_struct*()`.
- User memory callbacks receive a dummy `png_struct` carrying `mem_ptr` during initial structure creation/destruction before a real `png_struct` exists.

## Research Notes

For callers, the important contract is that all libpng-owned allocations should flow through this file so custom allocators, fatal/nonfatal allocation policy, and platform-specific allocation limits remain consistent.
