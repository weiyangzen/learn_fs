# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/timehist.c

Implements an exponential-bucket histogram for `struct timeval` values.

Core behavior:
- `timehist_setup` allocates a histogram with `NUM_BUCKETS_HIST` buckets and initializes bucket ranges.
- Bucket setup starts at zero and doubles the upper bound each bucket; the first bucket is `[0, 1 usec]`, then exponential growth.
- `timehist_insert` increments the first bucket whose upper bound is greater than or equal to the inserted value, falling back to the final bucket.
- `timehist_clear` zeros counts.
- `timehist_print` prints nonempty buckets to stdout.
- `timehist_log` logs quartiles and nonempty bucket ranges.
- `timehist_quartile` estimates a percentile by locating the bucket containing the requested item position and linearly interpolating within that bucket.
- `timehist_export` and `timehist_import` copy counts to/from a `long long` array.

Important details:
- Quartile estimation returns zero if fewer than four observations are present.
- Uses `timeval_smaller` from `timeval_func.c`.
- Not internally locked; callers must synchronize if shared.
