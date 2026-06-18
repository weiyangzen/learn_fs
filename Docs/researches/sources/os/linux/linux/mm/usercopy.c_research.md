# File Research: sources/os/linux/linux/mm/usercopy.c

This file implements hardened usercopy validation for `copy_to_user()` / `copy_from_user()` paths. Its role is defensive: reject kernel text exposure, invalid addresses, stack-frame misuse, and heap-object copies outside allocator-approved ranges.

Key elements:
- `check_stack_object()` classifies a copy range as off-stack, valid stack frame, valid stack range, or bad stack. It uses `task_stack_page(current)`, `THREAD_SIZE`, `arch_within_stack_frames()`, and optionally `current_stack_pointer`.
- `usercopy_abort()` reports whether the operation is kernel memory exposure or overwrite, then calls `BUG()`.
- `check_kernel_text_object()` blocks copies overlapping `_stext.._etext` and, when present, the linear alias returned by `lm_alias()`.
- `check_bogus_address()` catches wraparound ranges and `NULL` / zero-size allocation sentinel pointers.
- `check_heap_object()` validates kmap, vmalloc, direct-map, slab, and compound-page cases. Slab objects defer to `__check_heap_object()`, while compound pages are bounded by `page_size()`.
- `__check_object_size()` is the exported central validator. It skips zero-length copies, runs bogus-address checks, stack checks, heap checks, then kernel-text checks.
- `validate_usercopy_range` is a static branch configured by `CONFIG_HARDENED_USERCOPY_DEFAULT_ON` and the `hardened_usercopy=` boot option.

Important dependencies:
- Slab allocator usercopy metadata via `__check_heap_object()`.
- Architecture stack-frame support via `arch_within_stack_frames()`.
- vmalloc metadata via `find_vmap_area()`.
- kernel section symbols `_stext` and `_etext`.

Research notes:
- The code deliberately allows non-compound direct-map pages without exact boundary validation, because such pages may be part of larger allocations.
- vmalloc checking is skipped while page faults are disabled.
- The failure mode is intentionally fatal; violations are treated as kernel corruption/security bugs, not recoverable syscall errors.
