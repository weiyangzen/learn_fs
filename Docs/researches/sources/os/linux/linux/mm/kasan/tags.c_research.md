# File Research: sources/os/linux/linux/mm/kasan/tags.c

## Role

Shared initialization and allocation/free stack tracking for tag-based KASAN modes.

## Key Functions

- Parses `kasan.stacktrace=off|on` and `kasan.stack_ring_size=<entries>`.
- Defines `kasan_flag_stacktrace` as a static key controlling alloc/free stack collection.
- `kasan_init_tags()` applies boot-time stacktrace policy and allocates the stack ring from memblock, defaulting to `32K` entries.
- `save_stack_info()` saves an allocation or free stack to stack depot and records it in the global ring.
- Ring updates use a busy sentinel plus compare-exchange to avoid readers observing partially written entries.
- Old stack depot handles are dropped after replacement.
- `kasan_save_alloc_info()` and `kasan_save_free_info()` record alloc/free events for later tag-mode report reconstruction.

## Dependencies

Uses memblock allocation, stack depot, static keys, atomic ring position, scheduler clock/task state through KASAN track helpers, and slab cache object sizes.

## Research Notes

This file is the source of allocation/free context used by `report_tags.c`. Because tag modes do not encode rich object state in poison bytes, recent ring history is essential for classifying tag mismatches into use-after-free or out-of-bounds reports.
