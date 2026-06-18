# sources/test-tools/stress-ng/core-affinity.c

Purpose: CPU affinity parsing, application, migration, and usable-CPU enumeration for stress-ng.

Important APIs and control flow: `stress_affinity_parse_cpu` accepts comma tokens for numeric ranges, `odd`, `even`, `all`, `random`, and Linux topology selectors (`packageN`, `clusterN`, `dieN`, `coreN`); `stress_topology_set_get` reads sysfs topology CPU lists and deduplicates CPU sets; `stress_affinity_cpu_set` applies parsed affinity; `stress_affinity_change_cpu` changes worker CPU when `OPT_FLAGS_CHANGE_CPU` is set; `stress_affinity_cpus_get/free` allocates and releases usable CPU arrays.

State and persistence: stores the last applied process CPU set in file-static `stress_affinity_cpu_set_val`; changes kernel scheduler affinity for the current process but writes no files.

Dependencies and integration: gated by `sched_getaffinity`, `sched_setaffinity`, `cpu_set_t`, `/sys/devices/system/cpu`, random MWC helpers, global `g_opt_flags`, and CPU count helpers.

Risks and test signals: exits the process on invalid user input; assumes topology files exist and fit parser expectations; CPU_SETSIZE can truncate very large CPU numbers. Signals include parsing edge cases, topology selectors, affinity changes, and fallback behavior when affinity is unsupported.
