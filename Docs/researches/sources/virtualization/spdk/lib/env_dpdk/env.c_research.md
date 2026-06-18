# File Research: sources/virtualization/spdk/lib/env_dpdk/env.c

Implements SPDK environment wrappers over DPDK allocation, memzone, mempool, timing, affinity, ring, and memory-stat APIs.

Allocation wrappers use DPDK malloc/zmalloc/realloc/free with cache-line minimum alignment and optional NUMA fallback unless `mem_enforce_numa()` has been enabled. DMA allocation is the same allocator with SPDK DMA/share flags. Memzone reservation translates SPDK flags to DPDK memzone flags, zeroes successful reservations, and supports aligned or cache-line-aligned variants.

Mempool wrappers create DPDK mempools with capped per-lcore cache size, optional object constructors, optional NUMA fallback, and wrappers for get/put bulk, count, object iteration, memory-region iteration, lookup, and free. Ring wrappers create exact-size DPDK rings with SP/SC, MP/SC, or MP/MC flags and auto-generated names.

Other responsibilities include process-primary detection, tick/timer wrappers, microsecond delay, pause, thread unaffinitization and scoped unaffinitized callback execution, DPDK memory-stat dump/get APIs, thread id retrieval, and NUMA-enforcement enablement.
