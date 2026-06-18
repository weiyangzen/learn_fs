# sources/test-tools/stress-ng/core-helper.c

## Purpose

This broad helper module centralizes miscellaneous platform, process, formatting, diagnostic, and runtime utilities used across stress-ng. It handles CPU counts, load averages, parent-death signaling, dumpability, timer slack, process names, build/run info, compiler and uname strings, size formatting, executable path discovery, warn-once state, unused UID/PID probing, tty sizing, retry decisions, sysctl/MSR access, process diagnostics, machine ID synthesis, metric initialization, zero-buffer tests, and environment preservation.

## Important APIs, Types, And Functions

Public constants `stress_ascii64` and `stress_ascii32` provide character tables for generated names. System information APIs include `stress_cpus_online_get`, `stress_cpus_configured_get`, `stress_ticks_per_second_get`, `stress_load_average_get`, `stress_cpu_get`, `stress_compiler_get`, `stress_uname_info_get`, `stress_kernel_release_get`, `stress_hostname_length_get`, and `stress_machine_id_get`.

Process and runtime APIs include `stress_parent_died_alarm`, `stress_process_dumpable`, `stress_timer_slack_set`, `stress_proc_name_init`, `stress_proc_name_raw_set`, `stress_proc_name_set`, `stress_proc_name_scramble`, `stress_proc_state_set`, `stress_exec_text_addr`, `stress_is_dev_tty`, `stress_redo_fork`, `stress_process_info`, `stress_no_return`, and `stress_make_it_fail_set`.

Formatting and utility APIs include `stress_munge_underscore`, `stress_strcmp_munged`, `stress_uint64_zero_get`, `stress_null_get`, `stress_little_endian`, `stress_buildinfo`, `stress_yaml_buildinfo`, `stress_runinfo`, `stress_yaml_runinfo`, `stress_uint64_to_str`, `stress_const_optdup`, `stress_warn_once_hash`, `stress_unused_uid_get`, `stress_unused_racy_pid_get`, `stress_clear_warn_once`, `stress_flag_permutation`, `stress_exit_status`, `stress_proc_self_exe_get`, BSD sysctl wrappers, `stress_x86_readmsr64`, `stress_random_small_sleep`, `stress_yield_sleep_ms`, `stress_zero_metrics`, `stress_data_is_not_zero`, and `stress_env_ld_library_path_get`.

## Control Flow

Many getters cache successful results in static variables. Process-name functions either preserve names when `OPT_FLAGS_KEEP_NAME` is set, scramble names when `OPT_FLAGS_RANDPROCNAME` is set, or format names from program/stressor state. Build and run info functions are gated by logging flags or YAML output handles. `stress_warn_once_hash` hashes filename plus line, acquires the shared warn-once lock, linearly probes the shared hash array, and records first use. UID discovery enumerates passwd entries, sorts UIDs, and caches a gap. PID discovery optionally forks and reaps a child, then falls back to random PID probes and `/proc/sys/kernel/pid_max`.

## State And Persistence Behavior

State includes cached CPU counts, tick rate, unused UID, warn-once hashes in `g_shared`, global process name side effects, core dump filter settings, timer slack, kernel warn-once clearing, and static buffers returned by compiler, uname, libc, memory, and formatting helpers. Several helpers intentionally affect the process or kernel-visible state rather than returning pure values.

## Dependencies And Integration Points

The module integrates with git version metadata, capabilities, CPU cache/NUMA helpers, hash functions, sorting, filesystem and memory helpers, logging/YAML output, global option flags, shared memory, locks, random number utilities, shim wrappers, BSD sysctl, Linux `/proc`, Linux `/sys`, `prctl`, `procctl`, uname, sysinfo, pwd database access, and x86 MSR devices. It is a foundational dependency for many other core modules.

## Risks And Test Signals

Risks include non-reentrant static buffers, platform-specific stubs returning zeros, racy unused PID/UID guesses, process-name changes affecting external tooling, and shared warn-once lock availability during early startup. Test signals include stable CPU/load fallbacks, valid YAML output, correct underscore/dash comparison, warn-once suppression across repeated calls, sane size formatting, executable path discovery on each supported OS, fork retry behavior near timeout, process diagnostic output on Linux, and no crashes when optional platform features are absent.
