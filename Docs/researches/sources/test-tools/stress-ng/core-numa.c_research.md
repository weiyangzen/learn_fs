# sources/test-tools/stress-ng/core-numa.c

Purpose: provides NUMA node discovery, node-mask allocation, memory-policy binding, and random page placement helpers.

Important APIs/functions: `stress_numa_count_mem_nodes`, `stress_numa_mask_nodes_get`, `stress_numa_next_node`, `stress_numa_mask_alloc/free`, `stress_numa_randomize_pages`, `stress_numa_nodes`, `stress_set_mbind`, and `stress_numa_mask_and_node_alloc`.

Control flow: discovery parses `Mems_allowed` from `/proc/self/status` backwards. Mask allocation sizes bitmaps by discovered max node. On Linux with mempolicy syscalls, randomization divides a buffer into bounded chunks and calls `mbind(MPOL_BIND|MPOL_MF_MOVE)`. `stress_set_mbind` parses comma/range syntax and applies `set_mempolicy`. Unsupported builds provide stubs.

State/persistence: caches node count in `stress_numa_nodes`; allocates caller-owned masks; changes process memory policy and can migrate pages.

Dependencies/integration: Linux procfs and mempolicy syscalls through shims, MWC random numbers, option settings, bit macros, and stressor instance metadata.

Risks: parser exits on invalid `--mbind`; procfs parsing is Linux-specific; page migration can fail silently in randomization; chunk heuristics trade coverage for setup cost; cached node count can stale after hotplug.

Test signals: single/multi-node systems, cpuset-restricted mems, invalid ranges, unsupported builds, page migration permissions, and stressors with NUMA flags.
