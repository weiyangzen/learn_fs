# sources/test-tools/stress-ng/stress-numacopy.c

## Purpose
`stress-numacopy.c` implements the `numacopy` stressor. It allocates one page per NUMA node, binds each page to a target node, repeatedly copies data between every node pair, optionally changes CPU affinity, and reports page fill/copy rates and a per-node copy-rate table.

## Important APIs, Types, and Functions
The exported `stress_numacopy_info` is a `CLASS_CPU | CLASS_MEMORY | CLASS_OS` stressor with `VERIFY_ALWAYS` and options `numacopy-affinity` and `numacopy-mode`. `stress_numacopy_metric_t` tracks duration and rate per node pair. `stress_numacopy_cpus_t` stores CPUs associated with a NUMA node. `stress_numacopy_mode_t` and `stress_numacopy_affinity_t` define option tables. `stress_numacopy_exercise()` performs the copy workload and optional affinity switching. `stress_numacopy_affinity_supported()` checks scheduler affinity support. `stress_numanode_cpus()` parses sysfs `cpulist` files. `stress_numacopy()` allocates memory, binds pages, runs the workload, reports metrics, and cleans up.

## Control Flow
The stressor reads mode and affinity options, validates affinity support, discovers NUMA nodes, limits to 64 nodes, optionally builds a per-node CPU list, allocates a metrics matrix sized `nodes * nodes`, maps a pointer array and a local page, then maps one private page per NUMA node. Each node page is bound with `shim_mbind()` using the selected memory policy mode and `MPOL_MF_MOVE | MPOL_MF_STRICT`.

After synchronized start, the run loop calls `stress_numacopy_exercise()`. That function periodically changes CPU affinity according to the selected policy: current node, next node, previous node, random CPU, or none. For every source node and destination node pair it fills the local page, copies to source then destination, verifies the first byte, then fills and copies in the reverse direction. It accumulates per-pair duration and global copy/fill operation counts and increments the bogo counter. Instance zero prints a copy-rate matrix and the stressor publishes aggregate pages-filled and pages-copied metrics.

## State and Persistence
The stressor creates anonymous mappings for the page pointer array, local page, and per-node pages, all unmapped during cleanup. CPU affinity changes affect the stressor process while it runs; the code does not restore the original affinity before exit. Metrics live in process memory until reported into shared stats. It reads NUMA CPU topology from sysfs and does not write durable state.

## Dependencies and Integration Points
This Linux-oriented stressor requires `mbind` syscall support and NUMA mask helpers. It optionally depends on `sched_getaffinity` and `sched_setaffinity`, sysfs node CPU lists, and mempolicy constants such as `MPOL_BIND`, `MPOL_INTERLEAVE`, `MPOL_PREFERRED`, and `MPOL_WEIGHTED_INTERLEAVE`. It integrates with stress-ng target clones, mmap population, memory naming, memory usage reporting, bogo counters, metrics, logging, settings, and process states.

## Risks
There are several implementation-sensitive areas. `numa_cpus` is allocated with `max_cpus` entries but indexed by NUMA node up to `num_numa_nodes`; systems with more nodes than configured CPUs could index beyond the allocation. In the page-binding loop, the NUMA mask is not cleared between nodes before `STRESS_SETBIT`, so later `mbind` calls may include all previous nodes rather than only the current node. `stress_numacopy_affinity_supported()` has a non-void function path under missing affinity APIs that logs but does not explicitly return a value. The cpulist parser stops when it reaches a non-digit separator and may not advance past commas, so multi-range lists can be underparsed. The stressor can print a large matrix and consume noticeable CPU and memory bandwidth on many-node systems.

## Test Signals
Run with `--numacopy 1 --timeout 1 --metrics` on single-node and multi-node systems. Cover each `--numacopy-mode` exposed at build time and each affinity mode, especially `node`, `next`, `prev`, and `random`. Use systems or mocks with comma-separated cpulists to validate parsing. Sanitizer or bounds-checking runs are valuable for the `numa_cpus` node-vs-CPU allocation risk.
