<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fork.c -->
# sources/test-tools/stress-ng/stress-fork.c Research

Purpose: implements the `fork` and `vfork` stressors. They repeatedly create short-lived child processes, optionally apply extra VM pressure, and verify that fork failures are limited to expected resource exhaustion cases.

Important APIs/types/functions: `stress_fork_info` and `stress_vfork_info` register the stressors, help text, options, classifiers, and optional verification. `fork_info_t` records child PID and saved errno. `stress_fork_fn()` is the shared engine for both `fork()` and `shim_vfork()`. `stress_fork_shim_exit()` exits through `__NR_exit` before falling back to `_exit()`. Linux builds include `stress_fork_maps_reduce()`, which parses `/proc/self/maps` and applies `madvise()`, `mincore()`, or `munmap()` to selected shared libraries.

Control flow: `stress_fork()` reads `fork-max`, `fork-pageout`, `fork-unmap`, and `fork-vm`, resolves maximize/minimize defaults, disallows simultaneous `fork-vm` and `fork-unmap`, forces libc symbol binding, synchronizes workers, and calls `stress_fork_fn()`. With `fork-unmap`, it runs the core loop in a subprocess so aggressive unmapping does not corrupt the long-lived stress-ng worker. `stress_vfork()` reads `vfork-max`, synchronizes, and calls the same engine with `STRESS_VFORK`. The engine batches up to `fork_max` children, waits for them, increments bogo operations for successful reaps, and checks failure errno under verification.

State and persistence: all child process state is transient. `info` is a static aligned PID/error array local to the worker. `stress_fork_maps_reduce()` affects the current process address space only. No durable files are created.

Dependencies and integration: depends on stress-ng shims for settings, process state, synchronization, OOM adjustment, capability dropping, waits, vfork, memory advice, KSM, and logging. It is classified as scheduler/OS and integrated through the global stressor table via exported `stressor_info_t` objects.

Risks: `fork-unmap` is intentionally dangerous and Linux-specific; the code mitigates it by isolating the core loop in a child process. `/proc/self/maps` parsing and shared-library name filters can become stale. Verification accepts `EAGAIN` and `ENOMEM` but reports other fork errors, so platform-specific failures may be noisy. `vfork()` semantics require the child to exit immediately, which the code enforces.

Test signals: useful signals are bogo operation progress, optional verification failures for unexpected fork errno, and correct cleanup of child processes. Run coverage should include plain `fork`, `vfork`, `fork-vm`, `fork-pageout`, and isolated `fork-unmap` on Linux.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fork.c -->
