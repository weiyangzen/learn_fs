# File Research: sources/os/linux/linux/mm/fail_page_alloc.c

## Purpose

Provides fault injection for page allocator failures. It lets tests or debug configurations simulate allocation failure based on configured fault attributes, GFP filters, and minimum allocation order.

## Configuration State

Static `fail_page_alloc` contains:

- `struct fault_attr attr`
- `ignore_gfp_highmem`, default true
- `ignore_gfp_reclaim`, default true
- `min_order`, default 1

Boot setup uses:

- `__setup("fail_page_alloc=", setup_fail_page_alloc)`

## Main Function

`should_fail_alloc_page(gfp_t gfp_mask, unsigned int order)` returns true when the current allocation should fail.

It refuses injection when:

- `order < min_order`
- `__GFP_NOFAIL` is set
- highmem allocations are ignored and `__GFP_HIGHMEM` is set
- reclaimable allocations are ignored and `__GFP_DIRECT_RECLAIM` is set

If `__GFP_NOWARN` is set, it passes `FAULT_NOWARN` to avoid noisy reporting and possible deadlock-prone logging.

The function is exposed to the error injection framework:

- `ALLOW_ERROR_INJECTION(should_fail_alloc_page, TRUE)`

## Debugfs Interface

Under `CONFIG_FAULT_INJECTION_DEBUG_FS`, `late_initcall(fail_page_alloc_debugfs)` creates:

- `fail_page_alloc/ignore-gfp-wait`
- `fail_page_alloc/ignore-gfp-highmem`
- `fail_page_alloc/min-order`

All are mode `0600`.
