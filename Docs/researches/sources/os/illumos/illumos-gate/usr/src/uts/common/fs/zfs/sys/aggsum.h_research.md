# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/aggsum.h

This header declares an aggregate counter structure designed to reduce contention by spreading deltas across per-bucket counters while maintaining global lower and upper bounds.

Key definitions:
- `aggsum_bucket_t` is cacheline-aligned and contains a mutex, signed delta, borrowed count, and padding.
- `aggsum_t` contains a global lock, lower and upper bounds, bucket count, and cacheline-aligned bucket array.
- The comment states the counter fans out over a selected number of CPUs.

Declared operations:
- `aggsum_init()` initializes an aggregate counter with a starting value.
- `aggsum_fini()` releases resources.
- `aggsum_lower_bound()` and `aggsum_upper_bound()` expose approximate bounds.
- `aggsum_compare()` compares aggregate state against a value, presumably using bounds before exact aggregation.
- `aggsum_value()` returns the aggregate value.
- `aggsum_add()` applies a signed delta.

Important role:
- This is a synchronization/data-structure interface for high-frequency counters where exact global updates would be too expensive on every modification.
