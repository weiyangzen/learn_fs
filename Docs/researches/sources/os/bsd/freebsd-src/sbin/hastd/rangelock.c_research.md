# File Research: sources/os/bsd/freebsd-src/sbin/hastd/rangelock.c

`rangelock.c` provides a small in-memory range lock table for HAST. It stores locked byte ranges as `struct rlock` entries in a `TAILQ`, protected only by caller-side synchronization.

The API allocates/frees a `struct rangelocks`, adds exact ranges as `[offset, offset + length)`, removes an exact matching range, and tests overlap with `rl_start < end && rl_end > offset`. Assertions check the container magic value and that deletes find an existing range.

This is a simple conflict-detection helper, not a blocking lock manager: it does not sleep, merge ranges, sort entries, validate overflow, or provide internal mutex protection.
