# File Research: sources/virtualization/nbdkit/filters/rate/bucket.c

This file implements the token bucket used by the rate filter. Buckets track a fill `rate`, burst `capacity_secs`, token `capacity`, current `level`, and the last update timestamp.

`bucket_init` sets capacity as `rate * capacity_secs`, starts the bucket full, and stores the current time. `bucket_adjust_rate` changes the fill rate and capacity while clamping the current level. `bucket_run` refills based on elapsed microseconds, deducts requested tokens if available, or empties the bucket and returns how many tokens remain unavailable along with an estimated sleep time.

`rate == 0` is the no-limit case and immediately returns no required sleep. Timing uses `gettimeofday`, so negative elapsed time from non-monotonic clock changes is clamped to zero. Debug logging is controlled by `-D rate.bucket=1`.
