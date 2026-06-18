# File Research: sources/os/bsd/freebsd-src/sys/sys/tim_filter.h

## Scope

This header defines a compact time-window filter abstraction used in the kernel to track minimum or maximum values over recent time. It provides 64-bit and smaller 32-bit variants, structure layouts, filter type constants, and kernel function prototypes.

## APIs And Constants

- Defines `NUM_FILTER_ENTRIES` as 3, with comments tying the current size to amd64 cache-line considerations.
- Defines `struct filter_entry` with 64-bit value and update time, packed.
- Defines `struct filter_entry_small` with 32-bit value and update time.
- Defines `struct time_filter` with current time limit and three 64-bit entries; in kernel builds it is cache-line aligned.
- Defines `struct time_filter_small` with current time limit and three 32-bit entries.
- Defines filter type constants `FILTER_TYPE_MIN` and `FILTER_TYPE_MAX`.
- Under `_KERNEL`, declares setup, reset, clock-forward/tick, min/max apply, reduce/increase, and inline getter functions for both normal and small variants.

## Control Flow And Integration

- Callers initialize a filter with a type and time window, update its clock, and apply values through min or max update functions.
- The first entry is treated as the current filtered value by `get_filter_value()` and `get_filter_value_small()`.
- Duplicated normal/small APIs avoid polymorphism in kernel C and save memory where 32-bit values are sufficient.
- Reduce/increase helpers adjust the tracked values while preserving the time-window model.

## Dependencies

- Includes `<sys/types.h>` and `<machine/param.h>` for fixed-width types and `CACHE_LINE_SIZE`.
- Function implementations live outside this header and are only declared for kernel builds.

## Risks And Invariants

- The normal and small APIs are intentionally separate; passing the wrong structure type to the wrong function can corrupt memory or produce invalid results.
- `NUM_FILTER_ENTRIES` affects structure size, cache behavior, and algorithm expectations.
- Packed 64-bit entries can have alignment implications on some architectures, mitigated in part by cache-line alignment of the containing kernel structure.
- Time values are 32-bit, so callers must use the implementation's expected wraparound semantics.
