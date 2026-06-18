# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpu_topology.h

Kernel CPU topology tree definitions and lookup API.

Key responsibilities:
- Defines `cpu_node_t` topology nodes with parent, children, child count, cpumask membership, level type, AMD compute unit ID, and physical memory value.
- Defines topology levels: package, chip, core, and thread.
- Provides `CPUSET_FOREACH` iteration macro over `ncpus`.
- Declares global topology metadata and root node.
- Declares lookup helpers for masks by level, CPU node by CPU ID/chip ID, highest node memory, and per-CPU HT/core/physical IDs.

Dependencies:
- Kernel/kernel-structures only for structs; kernel-only for externs/functions.
- Includes `sys/param.h` and `sys/cpumask.h`.

Notable risks:
- `child_node[MAXCPU]` fixes maximum fanout to global CPU count.
- Consumers must distinguish topology level types from CPU IDs and chip IDs.
