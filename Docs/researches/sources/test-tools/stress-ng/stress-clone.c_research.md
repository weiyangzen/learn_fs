<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clone.c -->
# sources/test-tools/stress-ng/stress-clone.c

## Purpose
Implements the `clone` stressor, rapidly creating and reaping clone/clone3 children with many flag combinations while measuring clone latency and exercising namespace, unshare, and LDT-related paths.

## Important APIs, Types, and Functions
`stress_clone_info` registers the stressor with `clone-max`. `stress_clone_shared_t` holds shared metrics and racy booleans proving child invocation and wait success. `stress_clone_t` stores a PID and stack per tracked clone. `stress_clone_new()`, `stress_clone_head_remove()`, and `stress_clone_free()` manage active/free lists. `clone_func()` is the child callback; `stress_clone_child()` performs clone/clone3 loops; `stress_clone()` wraps the work in `stress_oomable_child()`.

## Control Flow
The top-level stressor maps shared state, creates a metrics lock, computes flag permutations, lowers OOM preference for the parent, synchronizes, then runs the clone workload in an OOM-able child. The workload allocates a large mapping, creates clones until `clone-max` or low memory, chooses either table flags or permutations, tries clone3 when available, falls back to clone, reaps head entries on failure or pressure, and drains all children on exit.

## State and Persistence Behavior
State includes shared metrics mmap, a process-local active/free clone list with mmaped descriptors and embedded stacks, optional flag permutation memory, and child processes. No files persist. Cleanup reaps clone children, frees descriptor mappings, frees permutations, destroys process memory by exit, and unmaps shared state.

## Dependencies and Integration Points
Uses Linux/Unix clone APIs and shim clone3, stress-ng locks, mincore/mmap/OOM helpers, flag permutation, memory-low checks, unshare/setns/modify_ldt shims, waitpid with `__WCLONE`, process state, and metrics. It integrates with stress-ng OOMable child handling using `STRESS_OOMABLE_DROP_CAP`.

## Risks and Edge Cases
Clone flag combinations can fail with EPERM/EINVAL by design. Avoiding `CLONE_VM` prevents parent memory corruption. clone3 may be absent and is disabled after ENOSYS. Low-memory behavior must reap promptly. Racy shared booleans are used only as sanity evidence. Some clone flags alter wait semantics, so `__WCLONE` handling is important.

## Test Signals
Good signals include nonzero bogo progress, "microsecs per clone" metric, no failure that children terminated before invocation, clean reaping under low `--clone-max`, and graceful behavior when clone3 or namespace flags are unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clone.c -->
