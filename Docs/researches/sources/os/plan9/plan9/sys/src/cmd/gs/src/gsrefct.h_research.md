# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsrefct.h

Defines Ghostscript’s manual reference-counting helper macros.

Key definitions:
- `rc_header`: `ref_count`, owning `gs_memory_t *`, and free procedure.
- `rc_free_proc` signature macro.
- Debug trace hooks for init/free/increment/adjust.
- Initialization/allocation macros: `rc_init_free`, `rc_init`, `rc_alloc_struct_0`, `rc_alloc_struct_1`.
- Free macro: `rc_free_struct`.
- Count adjustment macros: `rc_increment`, `rc_allocate_struct`, `rc_unshare_struct`, `rc_adjust`, `rc_adjust_only`, `rc_decrement`, `rc_decrement_only`.
- Assignment helpers: `rc_assign`, `rc_pre_assign`.

Integration:
- Used by pattern instances in `gspcolor.h`/`gspcolor.c` and other shared objects.
- Relies on Ghostscript memory allocator and structure descriptors.

Risk notes:
- Macros mutate pointer arguments and can free objects; caller ordering matters.
- `rc_assign` increments source before decrementing destination to handle alias/last-reference cases.
- No thread-safety is provided.
