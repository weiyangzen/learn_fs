# sources/test-tools/syzkaller/prog/alloc_test.go

## Purpose

This file tests internal program memory allocation helpers.

## Important APIs, Types, And Functions

`TestMemAlloc` defines table-driven sequences of `noteAlloc` and `alloc` operations, checking sequential allocation, pre-reserved ranges, and alignment behavior. `TestVmaAlloc` creates a test target and random generator, then performs 30 VMA allocations as a smoke test.

## Control Flow, State, Dependencies, And Integration

`TestMemAlloc` uses negative `size` values to mean allocation requests and positive values to mean reservations. It expects exact addresses from `memAlloc.alloc`. `TestVmaAlloc` uses `testutil.RandSource`, so seeds are logged and can be fixed with `SYZ_SEED`.

## Risks And Test Signals

The memory allocation test catches bitmap scanning, granule rounding, and last-position alignment regressions. The VMA test mainly catches panics and gross bounds errors; it does not assert distribution or exact pages because allocation is randomized.
