# File Research: sources/os/linux/linux/mm/kmsan/core.c

## Role

Core KMSAN runtime library. It manages task contexts, poisoning and unpoisoning memory metadata, origin stack creation and chaining, metadata copying, range checks, and metadata-contiguity validation.

## Key State

- `kmsan_enabled` gates runtime behavior globally.
- `DEFINE_PER_CPU(struct kmsan_ctx, kmsan_percpu_ctx)` provides interrupt/NMI-safe context storage when `current->kmsan_ctx` is unavailable.
- Task creation clears the task KMSAN context and unpoisons `thread_info`.

## Poisoning and Origins

- `kmsan_internal_poison_memory()` saves an origin stack with optional use-after-free extra bits and fills shadow/origin metadata.
- `kmsan_internal_unpoison_memory()` clears shadow and origin metadata.
- `kmsan_save_stack_with_flags()` captures a bounded stack trace and stores it in stack depot with KMSAN extra bits.
- `kmsan_internal_chain_origin()` creates a chained origin record for stores of uninitialized values, preserving use-after-free state and bounding chain depth to `KMSAN_MAX_ORIGIN_DEPTH`.

## Metadata Mutation

- `kmsan_internal_set_shadow_origin()` fills shadow bytes and updates origin slots at `KMSAN_ORIGIN_SIZE` granularity.
- Origin updates preserve nonzero origins unless all corresponding shadow bytes are clear.
- Missing metadata is tolerated for untracked ranges, but checked operations warn if metadata was expected.

## Metadata Copying

- `kmsan_internal_memmove_metadata()` copies shadow/origin metadata with `memmove()` semantics.
- It handles overlapping ranges by choosing forward or backward iteration.
- If source metadata is unavailable, destination memory is treated as initialized.
- Nonzero source shadow bytes trigger origin chaining so reports can show store propagation history.
- It avoids repeatedly chaining identical adjacent origins by caching the previous old/new origin pair.

## Memory Checking

- `kmsan_internal_check_memory()` scans a range for poisoned shadow bytes.
- It groups consecutive poisoned bytes with the same origin and calls `kmsan_report()` for each group.
- It handles untracked pages by flushing any pending report and skipping the untracked chunk.
- `kmsan_metadata_is_contiguous()` verifies that metadata for a cross-page range is either entirely untracked or linearly contiguous in shadow and origin memory.

## Vmalloc Helper

- `kmsan_vmalloc_to_page_or_null()` accepts only vmalloc/module metadata addresses, maps them to pages, and rejects invalid PFNs.

## Dependencies

Uses stack trace/depot, preemption/interrupt helpers, vmalloc, highmem, page and zone helpers, slab internals, and KMSAN shadow APIs.

## Research Notes

This file contains KMSAN’s central metadata invariants. Most exported hooks eventually delegate here. The most important correctness properties are contiguous metadata, correct origin-slot handling for unaligned copies, bounded origin chains, and avoiding allocation/instrumentation recursion while creating stack-depot origins.
