# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_uarray.c

## Role

`cpu_uarray.c` implements a small per-CPU unsigned 64-bit array helper. It allocates storage for `nr_items` counters per CPU, aligned to `CUA_ALIGN`, and provides summation helpers.

## Functions

`cpu_uarray_size()` computes the allocation size as:

- rounded-up per-CPU item storage for `nr_items` `uint64_t` values,
- multiplied by `NCPU`,
- plus the `cpu_uarray_t` header.

`cpu_uarray_zalloc()` zero-allocates the computed structure, verifies the value array alignment, and records the item count.

`cpu_uarray_free()` frees a previously allocated structure using the recorded item count.

`cpu_uarray_sum()` sums one item index across CPUs from `0` to `ncpus - 1`, using `UINT64_OVERFLOW_ADD()` to preserve overflow behavior.

`cpu_uarray_sum_all()` sums every item for every CPU, also using overflow-aware addition.

## Research Notes

This is a utility file for per-CPU counters. It allocates for `NCPU` capacity but sums over current `ncpus`, so users should understand whether deleted or sparse CPU IDs matter for their accounting model. Index validation is done with `VERIFY3U(index, <, cua->cu_nr_items)`.
