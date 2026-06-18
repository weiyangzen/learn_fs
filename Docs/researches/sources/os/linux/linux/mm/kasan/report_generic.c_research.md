# File Research: sources/os/linux/linux/mm/kasan/report_generic.c

## Role

Generic shadow-memory KASAN report support. It classifies bugs from shadow byte values, derives allocation sizes from generic shadow metadata, prints decoded stack-frame object information, and exports compiler ASan report entry points.

## Key Functions

- `kasan_find_first_bad_addr()` walks generic shadow bytes from the accessed address until it finds the first poisoned granule.
- `kasan_get_alloc_size()` derives the real allocation size from slab object shadow bytes, including partial last granules.
- `get_shadow_bug_type()` maps generic poison values to bug classes such as slab/global/stack out-of-bounds, use-after-free, alloca out-of-bounds, and vmalloc out-of-bounds.
- `get_wild_bug_type()` classifies addresses without KASAN metadata as null pointer, user memory, or wild memory access.
- `kasan_complete_mode_report_info()` fills the bug type and, for slab objects, copies alloc/free tracks from KASAN object metadata.
- `kasan_metadata_fetch_row()` copies shadow bytes for the common metadata dump.
- `kasan_print_aux_stacks()` prints stored auxiliary work-creation stacks.
- Under `CONFIG_KASAN_STACK`, stack-frame descriptor parsing locates and prints the poisoned stack frame and local-object ranges.
- Exports `__asan_report_load{1,2,4,8,16}_noabort`, `__asan_report_store{1,2,4,8,16}_noabort`, and variable-size load/store report functions.

## Dependencies

Uses generic KASAN shadow mapping helpers, slab KASAN metadata, stack depot, task stack helpers, exported compiler instrumentation ABI, and slab internals.

## Research Notes

This is the most precise KASAN reporting mode because poison byte values encode the memory region state. It can distinguish many concrete failure modes directly from shadow memory and can decode compiler-generated stack metadata when stack instrumentation is enabled.
