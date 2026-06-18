# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/cpu_uarray.h

## Role

Defines an aligned per-CPU unsigned 64-bit array abstraction for scalable counters.

## Layout Model

- Each CPU’s counter block is aligned to `CUA_ALIGN` = 128 bytes.
- `CUA_CPU_STRIDE(nr_items)` rounds item count up to the 128-byte stride.
- `CUA_INDEX(nr_items, c, i)` maps CPU index and stat index to the flat array.
- `CPU_UARRAY_VAL(cua, cpu_index, stat_index)` accesses a specific value.

## Main Type

- `cpu_uarray_t`:
  - `cu_nr_items`: number of values per CPU.
  - padding to one alignment unit.
  - flexible `volatile uint64_t cu_vals[]`.

The struct itself is aligned to 128 bytes.

## Kernel API

- `cpu_uarray_zalloc(size_t, int)`
- `cpu_uarray_free(cpu_uarray_t *)`
- `cpu_uarray_sum(cpu_uarray_t *, size_t)`
- `cpu_uarray_sum_all(cpu_uarray_t *)`

Summation saturates at `UINT64_MAX`.

## Research Relevance

Useful for scalable per-CPU statistics and avoiding cacheline sharing in multi-socket systems. This pattern can affect filesystem and block-layer counters.
