# sources/test-tools/stress-ng/core-resctrl.c

Purpose: parses the `--resctrl` option, records cache/bandwidth partitions, mounts or finds the Linux resctrl filesystem when supported, creates partition groups, and assigns stressor PIDs to partitions.

Important APIs/types/functions: `stress_partition_info_t` stores partition name, number, cache level, node, bitmask, and bandwidth. `stress_resctrl_info_t` maps stressor instance ranges to partitions. `stress_resctrl_parse` is the option parser. `stress_resctrl_init` prepares mount/groups. `stress_resctrl_set` applies a matching partition to a stressor instance PID. `stress_resctrl_deinit` removes groups, frees parser state, and unmounts only mounts created by stress-ng.

Control flow: parsing duplicates the option string and mutates delimiters in place. Partition clauses such as `p1=1:l3:fff:20,` are parsed first and stored in a linked list. Stressor clauses resolve names through `stress_stressor_find`, parse instance lists/ranges or `all`, require `@pN`, reject duplicate/overlapping instance ranges, and increment `stress_resctrls_added`. On supported Linux/ARM builds, init searches `/proc/mounts` for an existing resctrl mount; if none exists it creates a temporary mount point and mounts via new mount API or `mount(2)`. It then creates `stress-ng-pN` directories. Applying a PID writes schemata cache masks, memory bandwidth lines, and the PID to `tasks`.

State and persistence: global linked lists hold parsed partitions and per-stressor maps. Supported runs may create directories under an existing resctrl mount or create a temporary mounted filesystem. Deinit attempts to remove created partition directories and unmount/remove the temporary mount point.

Dependencies/integration: depends on `core-setting`, `core-stressors`, filesystem helpers, mount APIs, `stress_fs_temp_path_get`, and generated `STRESSORS` enumeration ordering.

Risks: feature is currently gated to Linux/ARM with mount headers despite the interface being generic. Parser requires partition definitions before references. Cleanup ignores many removal failures, so externally busy resctrl groups may remain. Schemata format assumptions can break on kernel resctrl variants.

Test signals: parser unit cases for partitions, missing delimiters, duplicate ranges, undefined partitions, `all`, and cache-level defaults. Runtime tests need root/capability-controlled resctrl environments and cleanup verification after failed mount/group creation.
