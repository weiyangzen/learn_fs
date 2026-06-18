# File Research: sources/os/bsd/freebsd-src/sys/sys/smp.h

Kernel SMP topology, CPU iteration, startup, stop, and rendezvous interface.

Key responsibilities:
- Defines topology node types, hardware IDs, CPU IDs, `struct topo_node`, and scheduler `struct cpu_group`.
- Defines cache-sharing levels and CPU group flags for HTT/SMT/thread and NUMA node behavior.
- Declares topology construction, traversal, analysis, and scheduler topology allocation helpers.
- Exposes global CPU counts, CPU sets, domain sets, and SMP startup state.
- Defines CPU iteration macros/functions over non-absent CPUs.
- Declares machine-dependent MP startup/shutdown functions and CPU stop/restart/suspend/resume hooks.
- Declares rendezvous, quiesce, and cross-CPU fencing helpers.

Important patterns:
- Topology is represented both as a general tree (`topo_node`) and scheduler-oriented grouped masks (`cpu_group`).
- `CPU_ABSENT()` tests `all_cpus`, allowing sparse CPU ID maps.
- `smp_rendezvous*()` supports executing coordinated callbacks across selected CPUs.
- SMP-specific declarations are gated so uniprocessor kernels still expose safe common helpers.

Research relevance:
- Important for understanding CPU topology assumptions behind per-CPU data, SMR, scheduler behavior, and cross-CPU synchronization.
