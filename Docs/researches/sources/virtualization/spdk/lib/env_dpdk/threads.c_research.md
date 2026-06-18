# File Research: sources/virtualization/spdk/lib/env_dpdk/threads.c

Maps SPDK environment core/thread APIs onto DPDK lcore APIs.

Important behavior:
- Core queries wrap `rte_lcore_count`, `rte_lcore_id`, `rte_get_main_lcore`, and `rte_get_next_lcore`.
- NUMA queries wrap DPDK socket APIs.
- `spdk_env_get_cpuset()` builds an SPDK cpuset from active DPDK lcores.
- Linux SMT sibling discovery reads `/sys/devices/system/cpu/cpu%d/topology/thread_siblings` and parses it as an SPDK cpuset.
- Thread launch/wait use `rte_eal_remote_launch()` and `rte_eal_mp_wait_lcore()`.

Integration note: this file is the env layer that the event/reactor code uses to enumerate and launch one reactor per selected lcore.
