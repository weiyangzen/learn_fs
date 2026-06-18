# File Research: sources/os/linux/linux/mm/kmsan/hooks.c

## Role

KMSAN hooks for kernel subsystems. These functions connect KMSAN metadata updates to allocation/free paths, vmalloc/ioremap mapping, user copies, USB URBs, DMA transfers, and public KMSAN check/poison APIs.

## Allocation Hooks

- `kmsan_task_create()` initializes a task KMSAN context inside a runtime guard.
- `kmsan_task_exit()` disables KMSAN for the current task when exiting.
- `kmsan_slab_alloc()` poisons slab object memory unless the allocation is zeroed, constructed, RCU-typesafe, untracked, or inside KMSAN runtime.
- `kmsan_slab_free()` poisons freed slab objects as use-after-free origins unless constructor or RCU semantics prevent that.
- `kmsan_kmalloc_large()` and `kmsan_kfree_large()` mirror slab handling for large page-backed allocations.
- Free poisoning avoids reclaim allocations by using `GFP_KERNEL & ~__GFP_RECLAIM`.

## Vmalloc and I/O Mapping

- `vmalloc_shadow()` and `vmalloc_origin()` derive vmalloc/module metadata addresses with `kmsan_get_metadata()`.
- `kmsan_vunmap_range_noflush()` unmaps shadow and origin vmalloc metadata and flushes caches.
- `kmsan_ioremap_page_range()` allocates zeroed shadow/origin pages for ioremap mappings, maps them into metadata virtual ranges, handles partial failure cleanup, and flushes metadata ranges.
- `kmsan_iounmap_page_range()` unmaps and frees metadata pages for ioremap ranges.

## Usercopy and Memory Movement

- `kmsan_copy_to_user()` checks copied kernel bytes for uninitialized data after copy completion.
- If the target address is actually kernel memory on architectures without overlapping user/kernel address space, it copies metadata instead of reporting a user leak.
- `kmsan_memmove()` exports metadata movement for ordinary memmove-like operations.

## USB and DMA

- `kmsan_handle_urb()` checks outbound URB transfer buffers and unpoisons inbound buffers.
- `kmsan_handle_dma_page()` applies direction-specific checking/unpoisoning:
  - `DMA_TO_DEVICE`: check initialized.
  - `DMA_FROM_DEVICE`: unpoison after device writes.
  - `DMA_BIDIRECTIONAL`: check then unpoison.
  - `DMA_NONE`: no action.
- `kmsan_handle_dma()` ignores highmem physical addresses, converts lowmem to virtual addresses, and processes page-by-page to avoid crossing unrelated allocations.
- `kmsan_handle_dma_sg()` applies DMA handling over scatterlists.

## Public KMSAN API

- `kmsan_poison_memory()` can poison arbitrary memory but exits inside runtime to avoid stack-depot allocation deadlocks.
- `kmsan_unpoison_memory()` can run even from runtime because it does not allocate or call instrumented code.
- `kmsan_unpoison_entry_regs()` unpoisons interrupt/syscall entry registers.
- `kmsan_check_memory()` reports uninitialized bytes in a range.
- `kmsan_enable_current()` and `kmsan_disable_current()` manipulate the per-task disable depth.

## Dependencies

Uses slab internals, vmalloc mapping internals, user access state save/restore, USB, DMA direction, scatterlist APIs, and KMSAN core metadata routines.

## Research Notes

This file is the integration boundary between KMSAN and the rest of the kernel. It is deliberately careful about runtime recursion, constructor/RCU allocator semantics, device direction semantics, and user/kernel address-space ambiguity during copy-to-user handling.
