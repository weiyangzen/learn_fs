# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsrefct.h

Defines Ghostscript’s reference-counting support macros and `rc_header`.

Key concepts:
- Reference-counted objects embed `rc_header rc`.
- `rc_header` stores count, allocator, and free procedure.
- Allocation macros initialize refcounts at 0 or 1.
- Increment/decrement/adjust macros handle zero-count free behavior.
- Assignment macros increment the new value before decrementing the old value to avoid premature free.

Important APIs/macros:
- `rc_free_struct_only`
- `rc_init`, `rc_init_free`
- `rc_alloc_struct_0`, `rc_alloc_struct_1`
- `rc_increment`, `rc_decrement`
- `rc_adjust`, `rc_adjust_only`
- `rc_assign`, `rc_pre_assign`
- Debug tracing hooks under `DEBUG`.

The header warns about interaction between reference counting and finalization: finalizing free procs must free the containing object before decrementing referenced objects.
