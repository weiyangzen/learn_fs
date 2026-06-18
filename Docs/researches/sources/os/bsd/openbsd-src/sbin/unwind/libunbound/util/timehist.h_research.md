# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.h

Declares the time histogram API.

Key constants and structures:
- `NUM_BUCKETS_HIST` is 40.
- `struct th_buck`: lower bound, upper bound, and count.
- `struct timehist`: bucket count and bucket array pointer.

Public API:
- Lifecycle: `timehist_setup`, `timehist_delete`, `timehist_clear`.
- Data operations: `timehist_insert`, `timehist_quartile`.
- Output: `timehist_print`, `timehist_log`.
- Serialization: `timehist_export`, `timehist_import`.

Usage notes:
- Values are `struct timeval`.
- Percentile argument should be between 0 and 1; the implementation does not enforce this beyond its search behavior.
