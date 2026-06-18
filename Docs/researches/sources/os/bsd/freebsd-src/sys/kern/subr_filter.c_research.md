# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_filter.c

## Purpose
Implements rolling time-window min/max filters for 64-bit values and smaller 32-bit variants.

## Key Elements
- Setup/reset: `setup_time_filter()`, `setup_time_filter_small()`, `reset_time()`, `reset_time_small()`.
- Apply functions: `apply_filter_min()`, `apply_filter_max()`, and `_small` variants.
- Maintenance helpers: `check_update_times*()`, `tick_filter_clock*()`, `forward_filter_clock*()`.
- Manual adjustment: `filter_reduce_by*()`, `filter_increase_by*()`.

## Behavior
A filter maintains `NUM_FILTER_ENTRIES` value/time slots. Setup validates min/max type and time length, then initializes entries to either the maximum sentinel for min filters or zero for max filters.

Applying a new min or max updates all slots if the new value is better than the current best, updates a suffix of slots if it is better than later entries, and then ages entries using fractional time limits across the window. Clock ticking ages entries without a new measurement, but preserves the oldest worst value rather than replacing it with a synthetic zero. Manual increase/reduce helpers rewrite all slots to the adjusted current value and timestamp.

## Research Notes
The filter does not own a clock source. Callers provide `now` in arbitrary units, making this a reusable network/timing primitive rather than a wall-clock API.
