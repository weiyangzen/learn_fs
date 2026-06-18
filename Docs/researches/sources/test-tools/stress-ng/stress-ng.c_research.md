# sources/test-tools/stress-ng/stress-ng.c

## Purpose
`stress-ng.c` is the main program and orchestration layer for stress-ng. It parses global and stressor-specific options, builds the selected stressor list, prepares shared state, forks worker processes, manages synchronized starts and termination, aggregates counters and metrics, writes optional YAML output, and performs cleanup.

## Important APIs, Types, and Functions
The file defines process-wide globals such as `g_item_current`, `g_opt_timeout`, `g_opt_flags`, `g_pr_log_flags`, `g_stress_continue_flag`, `g_shared`, `g_error_env`, and `g_nowt`. It owns the static `stressors[]` table generated from the `STRESSORS` macro and the linked `stress_stressor_list_t` selection list. The PID-to-stats hash table maps child PIDs to `stress_stats_t` during reaping.

Key control functions include `stress_opts_parse()` for getopt dispatch, `stress_list_item_find()` and `stress_stressors_enable()` for list construction, `stress_shared_mmap()` for shared memory setup, `stress_stats_buffers_setup()` for assigning per-instance stats and metric buffers, `stress_run()` for forking all selected instances, `stress_child_run()` for the child lifecycle, `stress_stressors_wait()` and `stress_wait_status()` for reaping, `stress_metrics_set()` and `stress_metrics_dump()` for metric capture, and `main()` for end-to-end setup and teardown.

## Control Flow
`main()` fixes stressor names, initializes process naming and defaults, parses options, validates incompatible flags, applies ionice, scheduler, taskset, resctrl, timeout, random seed, NUMA mbind, job-file, logging, and class settings, then enables selected stressors. It excludes unsupported and pathological stressors, prepares signal handlers, chooses sequential, permutation, or parallel setup, allocates shared memory and locks, assigns stats buffers, starts auxiliary monitors, and finally calls the appropriate run mode.

`stress_run()` iterates selected stressors and instances, initializes sync state and stats, forks each child, and stores the child PID in the hash table. Children call `stress_child_run()`, which applies scheduler settings, installs handlers, sets OOM and timer behavior, initializes `stress_args_t`, invokes the selected `stressor_info_t->stressor`, records counters and checksums, gathers rusage, and exits with a stress-ng status code. The parent waits, maps statuses to pass/fail/skipped/metrics states, optionally aborts all workers on failure, and later dumps metrics and subsystem reports.

## State and Persistence
Most runtime state is in anonymous shared mappings rooted at `g_shared`, including per-instance `stress_stats_t`, shared helper pages, lock-backed shared heap, cache buffers, counters, checksum mappings, warning hashes, port maps, and optional perf, thermal, and RAPL data. The program also uses process-local linked lists, option settings, signal flags, and PID hash chains. Durable outputs are limited to configured logs, syslog, optional YAML, and stressor-created external artifacts elsewhere in the tree. Cleanup unmaps shared regions, destroys locks, frees stressor lists, closes logs, and exits with a status reflecting success, no resources, bad metrics, or core failure.

## Dependencies and Integration Points
This file integrates nearly every core module: options, settings, logging, locks, shared heap, memory, mmap, scheduler, affinity, cpuidle, ftrace, perf, klog, vmstat, smart, thermal zones, RAPL, resctrl, signals, OOM handling, job parsing, and stressor registration. Stressor implementations depend on the `stress_args_t` initialized here, shared bogo counter helpers from the header, `stress_metrics_set()`, and lifecycle states emitted through `stress_proc_state_set()`.

## Risks
The main risks are orchestration complexity and signal/fork interactions. Shutdown uses global flags, alarms, process kills, child wait state, and shared counters; regressions can leave workers running or misclassify exits. Metrics rely on child updates to shared memory plus checksum mirrors; forced kills can make counters untrustworthy. Option parsing binds an `-ops` option to `g_item_current`, so command ordering matters for associating operation limits. Several cleanup labels assume earlier initialization state is consistent. `stress_stats_hash_table_alloc()` sizes the hash table from the number of instances, so a zero-instance path must not reach PID hashing. The run modes adjust per-instance bogo limits differently, which is important for tests.

## Test Signals
High-value signals include compile coverage with optional subsystems enabled and disabled, `--help`, `--stressors`, `--verifiable`, invalid option combinations, dry-run, sequential, parallel, random, permutation, class selection, exclude and with lists, timeout behavior, abort-on-failure, YAML output, metrics output, and unsupported-stressor paths. Runtime tests should verify no child processes remain after SIGINT, SIGALRM timeout, and early stressor failure. Metrics tests should include a stressor that emits misc metrics and a forced-kill scenario that marks metrics untrustworthy.
