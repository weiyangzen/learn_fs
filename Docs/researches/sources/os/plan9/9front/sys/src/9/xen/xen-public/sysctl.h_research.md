# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/sysctl.h

Purpose: Xen public system-control ABI for node control tools. It is explicitly gated to `__XEN__` or `__XEN_TOOLS__` and defines `xen_sysctl` operations for host console, trace buffers, physical host info, scheduler info, performance counters, domain lists, debug keys, CPU info, heap availability, power management, page offlining, lock profiling, topology/NUMA info, CPU pools, scheduler tuning, and coverage data.

Key interfaces:
- `XEN_SYSCTL_INTERFACE_VERSION`.
- Many operation structs, including `xen_sysctl_readconsole`, `xen_sysctl_tbuf_op`, `xen_sysctl_physinfo`, `xen_sysctl_getdomaininfolist`, `xen_sysctl_get_pmstat`, `xen_sysctl_pm_op`, `xen_sysctl_page_offline_op`, `xen_sysctl_lockprof_op`, `xen_sysctl_topologyinfo`, `xen_sysctl_numainfo`, `xen_sysctl_cpupool_op`, `xen_sysctl_scheduler_op`, `xen_sysctl_coverage_op`.
- Top-level `xen_sysctl` command union with 128-byte padding.

Integration notes: Depends on `xen.h` and `domctl.h`; not ordinary guest ABI.

Risk/attention points: The header enforces control-tool-only use via preprocessor error. Any 9front build path including it must define the correct Xen tool/hypervisor macros.
