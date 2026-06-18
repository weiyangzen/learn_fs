# sources/test-tools/stress-ng/stress-ng.h

## Purpose
`stress-ng.h` is the central public header for the stress-ng source tree. It establishes feature-test macros, compiler detection, standard includes, common constants, stressor classes, process and statistics data structures, the shared memory ABI, global variables, bogo counter helpers, metric types, and exported core entry points used by individual stressors.

## Important APIs, Types, and Functions
The header defines exit codes (`EXIT_NO_RESOURCE`, `EXIT_NOT_IMPLEMENTED`, `EXIT_METRICS_UNTRUSTWORTHY`), stressor lifecycle states, class bits, memory units, operation limits, and bit helpers. Core data types include `stress_pid_t` for process tracking, `stress_counter_t` for bogo counters, `stress_args_t` for the per-stressor runtime contract, `stress_list_item_t` for selected stressors, `stress_metrics_info_t` and `stress_metrics_desc_t` for metrics, `stress_stats_t` for per-instance accounting, `stress_shared_t` for process-shared state, `stressor_info_t` for each stressor module's exported metadata, and `stress_stressor_t` for the registry.

Inline helpers such as `stress_continue_flag()`, `stress_continue_set_flag()`, `stress_bogo_stop()`, `stress_bogo_add()`, `stress_bogo_inc()`, `stress_bogo_set()`, `stress_force_killed_bogo()`, `stress_bogo_inc_lock()`, and `stress_instance_zero()` are used throughout stressor implementations. Exported functions include `stress_opts_parse()`, `stress_shared_readonly()`, `stress_shared_unmap()`, `stress_system_memory_info_log()`, `stress_metrics_set()`, `stress_stressor_find()`, `stress_bogo_max_ops_zero()`, and `stress_args_pid_find()`.

## Control Flow
The header does not run control flow directly, but it defines the contracts used by `stress-ng.c` and all stressors. The central loop contract is `stress_continue(args)`, which checks whether the local bogo counter is below `args->bogo.max_ops`; global termination is handled by `g_stress_continue_flag` and `stress_continue_set_flag()`, which also zeros all max-op counters. Bogo helpers toggle `counter_ready`, issue memory barriers, update counters, and mark readiness, enabling the main process to detect partially updated counters.

## State and Persistence
The important persistent runtime state is represented by `stress_shared_t`, an mmap-shared structure containing shared helper pages, heap, locks, instance counters, subsystem buffers, warning hashes, atomic scratch space, synchronization data, checksum mirrors, and a flexible array of `stress_stats_t`. This is not durable across runs, but it is the in-memory ABI between parent and child processes. The header also declares global process state stored in `stress-ng.c`.

## Dependencies and Integration Points
`stress-ng.h` includes `config.h`, standard C/POSIX headers, platform headers, and many core stress-ng headers: version, attributes, assembly, options, settings, signals, stack, logging, locks, memory, random, scheduler, stressor registry, sync, shims, time, helpers, and filesystem. Every stressor includes this header and exports a `stressor_info_t` referenced by the `STRESSORS(STRESSOR_INFO)` macro expansion. The header also provides compile-time portability shims for compilers, libc variants, feature-test macros, `MAP_ANONYMOUS`, `PATH_MAX`, branch prediction, and deprecated direct filesystem calls.

## Risks
Because this header is included broadly, changes to structure layout, macros, or inline helpers have tree-wide impact. `stress_shared_t`, `stress_args_t`, and `stress_stats_t` changes affect parent/child shared memory assumptions. Bogo counter helpers are intentionally lightweight but not fully atomic; they rely on memory barriers and a readiness flag rather than locks in the common path. The `stress_continue(args)` macro checks only the per-stressor counter limit, so stressors that do not also inspect `stress_continue_flag()` may not react immediately to global shutdown unless `stress_bogo_max_ops_zero()` has propagated. Feature-test macro changes can alter libc declarations and build behavior across platforms.

## Test Signals
Any edit here should trigger broad build coverage. Useful tests are full compilation with several compiler/libc combinations, stressor smoke runs that exercise bogo counters, metrics emission, signal shutdown, shared-memory allocation and unmapping, and optional subsystem toggles. ABI-sensitive changes should be checked with representative stressors that fork children, spawn threads, emit metrics, use shared helper pages, and run under timeout.
