# File Research: sources/os/linux/linux/mm/kfence/kfence_test.c

## Role

KUnit test suite for KFENCE. It exercises pool allocation, object placement, canary corruption, out-of-bounds detection, use-after-free, invalid free handling, cache behavior, and stack-reporting assumptions.

## Key Test Infrastructure

- Uses KUnit expectations and KFENCE test-only exported symbols.
- Test build flags preserve frame pointers and disable sibling-call optimization to make stack traces stable.
- Allocates through slab/KFENCE paths and validates whether returned objects are KFENCE objects.
- Uses controlled invalid accesses and frees to trigger KFENCE reports.
- Tests validate counters, object metadata, allocation/free stack capture, and page-protection behavior where possible.

## Coverage Themes

- Basic guarded allocation and freeing.
- Object size and `ksize` behavior.
- Left/right object placement with canary redzones.
- Canary corruption detection on free.
- Out-of-bounds accesses into guard pages.
- Use-after-free detection after object page protection.
- Invalid free/double free reporting.
- Interaction with slab caches and constructor/initialization semantics.
- Behavior around disabled or skipped KFENCE allocation cases.
- Debug/report stack fidelity.

## Dependencies

Uses KUnit, slab allocation APIs, KFENCE public/test hooks, page-fault/report behavior, and compiler stack-frame preservation from the Makefile.

## Research Notes

The test file is intentionally coupled to KFENCE internals and report behavior. It is not a generic allocator test; it verifies that the sampled guarded allocator preserves slab-facing semantics while reliably detecting the specific memory safety classes KFENCE is designed for.
