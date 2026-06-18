# File Research: sources/os/bsd/freebsd-src/sys/sys/stats.h

## Purpose
`stats.h` defines FreeBSD's kernel/user statistics blob API: templates, value-of-interest stat specifications, typed storage, histogram and t-digest helpers, serialization, sampling controls, and inline update/fetch wrappers.

## Main Interfaces
- Stat types include VOI state, sum, max, min, histogram, and t-digest.
- Data types cover signed/unsigned 32/64-bit integers, long/unsigned long, fixed-point q32/q64 values, continuous/discrete histogram variants, and clustering t-digest variants.
- Defines typed storage structs for numeric values, histograms, t-digest centroids, t-digest trees, `voistatdata`, `voistatspec`, `statsblob`, `metablob`, and `statsblob_tpl`.
- Constructor macros create common stat specs such as `STATS_VSS_SUM`, `STATS_VSS_MAX`, `STATS_VSS_MIN`, histogram specs, t-digest specs, and user bucket arrays.
- ABI v1 functions allocate templates, add VOI stats, initialize/clone/snapshot/destroy blobs, render blobs to strings, visit blob entries, update VOIs, and fetch stat data pointers.
- Inline ABI-agnostic wrappers expose typed fetch and absolute/relative update helpers for integer, long, and fixed-point values.

## Implementation Notes
The blob ABI records version, endianness, flags, max size, current size, and opaque payload. Iteration uses `sb_visit` flags for first/last callback, VOI, and voistat boundaries. Histogram helpers support linear, exponential, linear-exponential, and user-defined buckets. T-digest helpers use array-based red-black trees, with diagnostic RB trees optionally present.

## Dependencies and Constraints
Includes `sys/limits.h` and conditionally `sys/tree.h` under `DIAGNOSTIC`. Non-kernel builds define `VNET` shims so template code can be shared with userland. Callers must match VOI dtype and stat dtype; typed fetch helpers return `EFTYPE` on mismatches.
