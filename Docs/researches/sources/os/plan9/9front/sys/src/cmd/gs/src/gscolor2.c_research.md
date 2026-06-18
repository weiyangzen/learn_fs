# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gscolor2.c

## Role

`gscolor2.c` implements Ghostscript Level 2 color operations: general `setcolorspace`/`setcolor`, Indexed color spaces, Indexed color lookup/remapping, serialization, and high-level device color-space inclusion.

This is rendering/color-space infrastructure, not filesystem code.

## Main Public Interfaces

- `gs_setcolorspace`
- `gs_currentcolorspace`
- `gs_setcolor`
- `gs_currentcolor`
- `lookup_indexed_map`
- `free_indexed_map`
- `alloc_indexed_map`
- `gs_cspace_build_Indexed`
- `gs_cspace_indexed_num_entries`
- `gs_cspace_indexed_value_array`
- `gs_cspace_indexed_set_proc`
- `gs_cspace_indexed_lookup`
- `gs_includecolorspace`

## Core Behavior

`gs_setcolorspace` rejects changes inside `cachedevice`, adjusts reference counts, installs the new color space, updates overprint if active, initializes the current color, releases the old current color and old color space, and invalidates device color.

`gs_setcolor` copies client color into graphics state, adjusts old/new color references, restricts values through the color-space type, and invalidates device color.

Indexed color-space support can use either:

- a byte string table owned externally
- an allocated `gs_indexed_map` palette/procedure object with reference-counted storage

The Indexed color type delegates installation, overprint, and concrete-space selection to its base space. Concretization looks up a palette entry into a `gs_client_color`, then concretizes in the base color space.

Serialization writes the base color space, high index, mode flag, and either mapped float values or byte table data.

`gs_includecolorspace` calls the current device’s `include_color_space` procedure for high-level output devices such as PDF.

## Dependencies

Uses color-space internals, pattern/color remapping, stream serialization, memory/refcount helpers, and device procedures.

## Notable Risks

- `gs_cspace_indexed_value_array` returns null when `use_proc` is true, which appears inconsistent with the header comment saying the function returns the cached-value array for procedure-based Indexed color spaces. Since the non-procedure path stores a byte table rather than a map, the implementation condition is suspect.
- The byte-table mode stores a caller-owned pointer; lifetime is external.
- `gs_cspace_build_Indexed` sets `hival = num_entries - 1`; a zero `num_entries` value would underflow.
