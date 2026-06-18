# File Research: sources/local-fs/squashfs-tools/squashfs-tools/nprocessors_compat.c

Implements cached `get_nprocessors()`. Linux uses `sched_getaffinity()` and `CPU_COUNT()` first, honoring CPU affinity/cgroup-like restrictions, then falls back to `sysconf(_SC_NPROCESSORS_ONLN)`.

Non-Linux uses `sysctl()` with `HW_AVAILCPU` if available, otherwise `HW_NCPU`. On failure it logs an error and defaults to one processor.

The static `processors` cache avoids repeated OS calls.
