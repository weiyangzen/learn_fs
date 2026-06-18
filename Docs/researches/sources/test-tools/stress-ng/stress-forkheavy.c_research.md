<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-forkheavy.c -->
# sources/test-tools/stress-ng/stress-forkheavy.c Research

Purpose: implements `forkheavy`, a scheduler/OS stressor that allocates many auxiliary resources and then rapidly forks and reaps many child processes, measuring fork latency under resource pressure.

Important APIs/types/functions: `stress_forkheavy_args_t` passes resource arrays, pipe size, and shared metrics into an OOMable child. `stress_forkheavy_t` and `stress_forkheavy_list_t` maintain active and free PID list nodes. `stress_forkheavy_new()`, `stress_forkheavy_head_remove()`, and `stress_forkheavy_free()` own that list. `stress_forkheavy_child()` performs the main fork/reap loop. `stress_forkheavy()` allocates resources/metrics and registers the OOMable execution. Options are `forkheavy-allocs`, `forkheavy-procs`, and `forkheavy-mlock`.

Control flow: the top-level stressor allocates a `stress_resources_t` array, maps shared metrics, creates a metrics lock, and invokes `stress_oomable_child(..., STRESS_OOMABLE_DROP_CAP)`. The child computes a minimum free-memory reserve, reads settings, optionally enables `MCL_FUTURE`, allocates resource pressure through `stress_resources_allocate()`, synchronizes with peer workers, then loops. If memory is not low and the active list is below `forkheavy-procs`, it appends a node, timestamps under the metrics lock, forks, updates metrics in the child, and exits. If fork fails or memory is low, it reaps the oldest child. Shutdown alarms and waits all remaining children, frees the PID lists, and releases allocated resources.

State and persistence: process state is in the per-worker global `forkheavy_list`, which is cleared before exit. Metrics live in shared anonymous memory and are reduced into a "microsecs per fork" harmonic metric. No files persist after the stressor.

Dependencies and integration: depends on core lock, mmap, OOM, and resource helpers. It uses stress-ng synchronization, settings, memory-limit checks, `stress_make_it_fail_set()`, bogo counters, and metrics.

Risks: high defaults can hit process limits, memory pressure, cgroup PID limits, or mlock restrictions. Metrics timing crosses a fork boundary and uses shared locking, so it is an approximate latency signal. The active list is global within the worker process; unexpected early exits before cleanup could leave children until parent death handling or alarms reap them.

Test signals: expected outputs are steady bogo progress and a nonzero microseconds-per-fork metric. Resource exhaustion should be handled by reaping rather than failing. Exercise minimize/maximize, explicit process limits, and `forkheavy-mlock` on systems with and without sufficient privileges.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-forkheavy.c -->
