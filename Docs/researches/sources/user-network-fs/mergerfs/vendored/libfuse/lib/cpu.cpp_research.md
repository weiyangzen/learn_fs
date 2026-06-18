<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.cpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.cpp

Purpose: This implementation provides CPU affinity and topology helpers for thread pinning.

Important functions: `CPU::getaffinity` reads the current process affinity mask with `sched_getaffinity`; `setaffinity` overloads set a pthread to a mask, one CPU, or a set of CPUs. `count` returns the number of CPUs in the current affinity mask. `cpus` returns allowed CPU IDs. `cpu2core` and `core2cpus` read `/sys/devices/system/cpu/cpuN/topology/core_id` to map logical CPUs to core IDs.

Control flow and state: no persistent state is stored. Each query reads the current affinity mask and, for topology, sysfs files. Topology loops stop early if a core_id file cannot be opened.

Risks and test signals: this implementation is Linux/sysfs oriented despite some FreeBSD include handling in the header. Ignoring `getaffinity` errors in `cpus` and topology functions can yield empty or partial maps. Tests should mock or run on systems with restricted affinity, missing sysfs topology files, hyperthreaded cores, and invalid CPU IDs for `setaffinity`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/lib/cpu.cpp -->
