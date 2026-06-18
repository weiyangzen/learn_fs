# sources/test-tools/stress-ng/core-cpu-cache.c

Purpose: discovers CPU cache topology/sizes and exposes cache query and flush helpers.

Important APIs and control flow: query path tries Linux sysfs cache indexes, auxv, x86 CPUID, and architecture fallbacks for SPARC, M68K, SH4, Alpha, RISC-V, OR1K, and Apple sysctl. Public helpers allocate full CPU cache details, find max cache level, retrieve cache by level/type, compute LLC or level sizes, free all allocations, and flush data cache using `clflushopt`, `clflush`, `__builtin___clear_cache`, or `shim_cacheflush`.

State and persistence: returns dynamically allocated cache structures owned by callers; reads sysfs/proc/device-tree/sysctl/CPUID but writes no durable state.

Dependencies and integration: depends on architecture headers, x86 asm, CPU feature checks, `stress_fs_*`, `scandir`, `getauxval`, sysctl helpers, and cache type structs from the header.

Risks and test signals: comments note an assumption of one data cache per CPU cache level; fallback data may be approximate; CPU hotplug and offline CPUs can affect discovery; allocation failures degrade to zero data. Signals are correct LLC/line-size values, leak-free `stress_cpu_cache_free`, and functioning cache flush paths.
