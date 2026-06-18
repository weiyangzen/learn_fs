# sources/test-tools/stress-ng/stress-memhotplug.c

Purpose: implements `memhotplug`, a privileged Linux stressor for memory hotplug sysfs state transitions. It repeatedly writes removable memory blocks offline and online, optionally while creating anonymous mappings to catch mapping faults during hotplug activity.

Important APIs/types/functions: `stress_mem_info_t` stores memory block name and timeout status; `stress_memhotplug_metrics_t` stores timing. `stress_memhotplug_supported()` requires `CAP_SYS_ADMIN`. `stress_memhotplug_removable()` reads `/sys/devices/system/memory/memory*/removable`. `stress_memhotplug_mem_toggle()` writes `offline` then `online` to a block's `state` file with a profiling timer. `stress_memhotplug_mem_online()` restores a block. SIGSEGV recovery uses `stress_segv_handler()`.

Control flow: the stressor installs SIGPROF/SIGSEGV handlers, opens the sysfs memory directory, counts removable blocks, stores names, synchronizes, sets a jump recovery point, then loops over blocks. For each block it optionally maps memory, attempts offline with timeout detection, unmaps, attempts online, records durations, and increments bogo ops. If every block times out, it tries to online all blocks.

State and persistence: this stressor mutates kernel memory block state and must restore all tracked blocks online in cleanup. It frees duplicated sysfs names, unmaps optional mappings, restores the old SIGSEGV handler, and reports online/offline timing metrics.

Dependencies/integration: Linux-only, sysfs memory hotplug ABI, `CAP_SYS_ADMIN`, `setitimer`, signal helpers, capability checks, mmap helpers, and metrics/options.

Risks/test signals: high-impact privileged operation; offlining memory can fail, stall, or disrupt workloads. Useful signals are skip without capability/removable entries, online/offline metrics, debug SIGSEGV count, all blocks restored online, and no lingering custom signal handler.
