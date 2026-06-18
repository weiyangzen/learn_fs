# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_cpu_topology.c

CPU topology discovery, tree construction, sibling mask query, and sysctl export for DragonFly BSD.

Key responsibilities:
- Builds a uniform topology tree from architecture-provided APIC/chip/core/thread ID helpers.
- Stores topology nodes in a static `MAXCPU` node array and exports `cpu_root_node`/`root_cpu_node`.
- Computes threads per core, cores per chip, physical package count, per-CPU physical/core/HT IDs, and sibling masks.
- Handles x86_64 AMD compute-unit reshaping when `fix_amd_topology()` reports applicable topology.
- Provides query helpers such as `get_cpu_node_by_cpuid()`, `get_cpumask_from_level()`, `get_cpu_node_by_chipid()`, `get_cpu_ht_id()`, `get_cpu_core_id()`, `get_cpu_phys_id()`, and `get_highest_node_memory()`.
- Builds `hw.cpu_topology` sysctls, including a printable topology tree, level descriptions, root members, and per-CPU physical/core sibling data.

Important behavior:
- Initialization runs at `SI_BOOT2_CPU_TOPOLOGY` using `naps + 1` as the assumed CPU count.
- Topology shape is inferred from BSP sibling relationships, then APIC IDs are walked in order to populate leaf CPU masks.
- Physical IDs are normalized into a compact range before being exposed for VM/scheduler use.

Dependencies:
- Depends on machine SMP helpers: `detect_cpu_topology()`, APIC ID lookup, chip/core/logical CPU ID accessors, and AMD topology fixups.
- Uses DragonFly cpumask macros and `sbuf` for sysctl string generation.

Notable risks:
- The builder assumes a mostly uniform topology; unusual heterogeneous CPU layouts may be represented poorly.
- `get_next_valid_apicid()` can return `-1` when no valid APIC ID is found, so correctness depends on architecture data and `assumed_ncpus` being consistent.
- Several output buffers are fixed-size strings sized from `MAXCPU`; very large CPU counts depend on those sizing assumptions.
