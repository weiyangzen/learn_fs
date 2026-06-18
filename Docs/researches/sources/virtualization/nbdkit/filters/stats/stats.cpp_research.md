# File Research: sources/virtualization/nbdkit/filters/stats/stats.cpp

This C++ filter records operation counts, byte totals, elapsed operation time, total runtime throughput, and optional request-size/alignment histograms for reads, writes, trims, zeroes, extents, cache, and flush. It requires `statsfile`, optionally appends with `statsappend`, and controls histogram verbosity with `statsthreshold`.

Global `nbdstat` structures hold per-operation counters and unordered-map histograms. A global pthread mutex protects all stats and output. `.get_ready` opens the report file with `O_CLOEXEC` and records start time; `.unload` prints totals and closes/free resources. Each operation callback timestamps before forwarding to `next`, then records only successful operations.

Histogram logic buckets request size by `floor(log2(size))` and alignment by trailing zero bits in the offset, with offset 0 treated as any alignment. Output includes cumulative alignment fixups and prints buckets until the configured percentile threshold is covered.

Risks and invariants: `print_threshold == 0` disables histogram allocation. `record_stat` degrades to basic counters after `std::bad_alloc`. Flush uses size 0 and therefore is not included in histograms. The code aborts if histogram per-bucket counts diverge from the operation total, treating that as internal corruption.
