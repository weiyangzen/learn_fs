# sources/test-tools/stress-ng/stress-numa.c

## Purpose
`stress-numa.c` implements the `numa` stressor. It exercises Linux NUMA memory policy syscalls by allocating a shared memory region, binding and moving pages among NUMA nodes, probing invalid syscall arguments, checking page data integrity, and recording NUMA hit/miss style metrics.

## Important APIs, Types, and Functions
The stressor exports `stress_numa_info` with `CLASS_CPU | CLASS_MEMORY | CLASS_OS`, `VERIFY_ALWAYS`, and options `numa-bytes`, `numa-shuffle-addr`, and `numa-shuffle-node`. `stress_numa_stats_t` stores aggregate `numa_hit` and `numa_miss` readings. `stress_numa_stats_read()` scans `/sys/devices/system/node/node*/numastat`. `stress_numa_check_maps()` inspects `/proc/self/numa_maps` for the node backing a mapping. `stress_numa()` allocates masks and memory, runs `get_mempolicy`, `set_mempolicy`, `mbind`, `migrate_pages`, `move_pages`, and metric collection.

## Control Flow
The stressor derives memory size from settings and instance count, allocates NUMA masks for available nodes, and maps arrays for page statuses, destination nodes, page pointers, and the data buffer. It reads baseline NUMA stats, synchronizes, chooses an initial node, and enters a loop. Each iteration probes current policy and invalid `get_mempolicy` cases, sets random or invalid policies, touches memory, gets CPU/node information, binds the buffer to a node with `mbind`, sets home nodes, exercises invalid `mbind` cases, optionally checks privilege behavior for `MPOL_MF_MOVE_ALL`, migrates process pages, and then repeatedly builds page and destination arrays for `move_pages`.

Within the `move_pages` section it can shuffle page addresses and destination nodes, writes each page's own address into the page for integrity checking, moves pages, checks `/proc/self/numa_maps` for the first buffer page, verifies page contents, and touches pages again. It also probes invalid `move_pages` calls such as bad PID, zero pages, invalid flags, invalid address, invalid destination node, and null nodes. After the loop it computes metrics from sysfs counters and mapping checks.

## State and Persistence
All mappings are anonymous and released before return. NUMA memory policy changes are process-local and end with process exit, though they can influence the stressor while it runs. Metrics are persisted to shared stats. The code reads sysfs and procfs but does not write durable files.

## Dependencies and Integration Points
This Linux-only stressor requires syscall numbers for `get_mempolicy`, `mbind`, `migrate_pages`, `move_pages`, and `set_mempolicy`, plus Linux mempolicy constants. It integrates with `core-numa` mask helpers, mmap population helpers, madvise helpers, stress-ng settings, capabilities, process states, memory usage reporting, bogo counters, and metrics.

## Risks
NUMA syscall behavior depends heavily on kernel config, cpuset/cgroup policy, permissions, and hardware topology. The stressor tolerates `ENOSYS`, `EIO`, and some permission failures, but unexpected errno values become failures. Memory size is rounded by page size and per-instance count, so many instances can still create significant memory pressure. Parsing `/proc/self/numa_maps` is format-sensitive. Data verification stops after repeated mismatches, which can indicate page movement corruption or writes through unexpected aliases.

## Test Signals
Run on a NUMA-capable Linux system with short timeouts and both shuffle options. Also run on a single-node or NUMA-disabled system to confirm skip behavior. Privileged and unprivileged runs should cover `MPOL_MF_MOVE_ALL` permission checks. Metrics should include NUMA hits/misses when sysfs is readable and checked-page percentage when `/proc/self/numa_maps` exposes matching entries.
