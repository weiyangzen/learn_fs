# File Research: sources/os/linux/linux/mm/vma_exec.c

This file contains exec-specific operations that are still purely VMA logic: creating the temporary initial stack VMA and relocating it downward during exec setup.

Functions:
- `relocate_vma_down()` shifts a VMA downward by `shift` bytes. It expands the VMA to cover both old and new ranges, moves page tables with `move_page_tables()`, frees obsolete PGD ranges with `free_pgd_range()`, and then shrinks the VMA to the new range with `vma_shrink()`.
- `create_init_stack_vma()` allocates and inserts the temporary initial stack VMA at `STACK_TOP_MAX - PAGE_SIZE .. STACK_TOP_MAX`, marks it anonymous, applies `VM_STACK_FLAGS | VM_STACK_INCOMPLETE_SETUP`, handles soft-dirty support, runs `ksm_execve()`, inserts the VMA, and initializes `mm->stack_vm` / `mm->total_vm`.

Important behavior:
- `relocate_vma_down()` requires the destination gap between new and old ranges to be empty and verifies this through the VMA iterator.
- It sets `pmc.for_stack = true`, making the page-table move stack-specific.
- On page-table move failure, cleanup is delegated to later process cleanup because partial movement may already have occurred.
- `create_init_stack_vma()` takes the mmap write lock killably and unwinds through `ksm_exit()`, unlock, and `vm_area_free()` on error.
- The stack is temporarily placed at the architecture’s maximum stack address rather than `STACK_TOP`, because final process attributes might not be configured yet.

Research notes:
- These helpers are intentionally documented as not general-purpose VMA relocation/creation APIs.
- The file depends on core VMA merge/shrink behavior from `vma.c` and allocation from `vma_init.c`.
